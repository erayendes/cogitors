#!/usr/bin/env python3
"""Run 1-3 independent CLI jobs; keep transcripts in a private temporary directory."""

import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time


EFFORTS = {
    "codex": {"low", "medium", "high", "xhigh", "max", "ultra"},
    "claude": {"low", "medium", "high", "xhigh", "max"},
    "antigravity": {"low", "medium", "high", "max"},
}
MAX_OUTPUT_BYTES = 5_000_000
MAX_ANTIGRAVITY_ARGV_BYTES = 250_000



def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key: " + key)
        result[key] = value
    return result


def load_jobs(path):
    with open(path, encoding="utf-8") as source:
        manifest = json.load(source, object_pairs_hook=unique_object)
    if not isinstance(manifest, dict) or set(manifest) != {"jobs"}:
        raise ValueError("manifest must contain only jobs")
    return validate_jobs(manifest["jobs"])


def validate_jobs(jobs):
    """Validate all jobs before starting any process; supply safe defaults."""
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= 3:
        raise ValueError("jobs must be a list of 1-3 jobs")
    allowed = {"agent", "cwd", "prompt", "access", "timeout_seconds", "context_only", "model", "effort"}
    seen, validated = set(), []
    for index, job in enumerate(jobs):
        if not isinstance(job, dict) or set(job) - allowed:
            raise ValueError("job %s has unknown fields or is not an object" % index)
        agent, cwd, prompt = (job.get(key) for key in ("agent", "cwd", "prompt"))
        if not isinstance(agent, str) or agent not in {"codex", "claude", "antigravity"}:
            raise ValueError("job %s has an invalid agent" % index)
        if agent in seen:
            raise ValueError("agents must be distinct")
        if not isinstance(cwd, str) or "\0" in cwd or not os.path.isabs(cwd) or not os.path.isdir(cwd):
            raise ValueError("job %s cwd must be an absolute existing directory" % index)
        if not isinstance(prompt, str) or not prompt.strip() or "\0" in prompt:
            raise ValueError("job %s prompt must be nonempty text without NUL" % index)
        access, context = job.get("access", "review"), job.get("context_only", False)
        timeout = job.get("timeout_seconds", 180)
        if access not in ("review", "edit") or type(context) is not bool or (context and access == "edit"):
            raise ValueError("job %s has invalid access/context_only settings" % index)
        if type(timeout) not in (int, float) or not 0 < timeout <= 3600:
            raise ValueError("job %s timeout_seconds must be > 0 and <= 3600" % index)
        normalized = dict(agent=agent, cwd=cwd, prompt=prompt, access=access,
                          context_only=context, timeout_seconds=timeout)
        if "model" in job:
            model = job["model"]
            if not isinstance(model, str) or not model.strip() or "\0" in model:
                raise ValueError("job %s model must be nonempty text without NUL" % index)
            normalized["model"] = model
        if "effort" in job:
            effort = job["effort"]
            if not isinstance(effort, str) or effort not in EFFORTS[agent]:
                raise ValueError("job %s effort is unsupported for %s" % (index, agent))
            normalized["effort"] = effort
        if agent == "antigravity" and len(prompt.encode("utf-8")) > MAX_ANTIGRAVITY_ARGV_BYTES:
            raise ValueError("job %s antigravity prompt exceeds safe argv limit (%s bytes)" % (index, MAX_ANTIGRAVITY_ARGV_BYTES))
        validated.append(normalized)
        seen.add(agent)
    return validated


def fingerprint(job):
    """Hash the validated request, including defaults and requested settings."""
    normalized = validate_jobs([job])[0]
    encoded = json.dumps(normalized, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def probe_antigravity():
    """Probe CLI startup requirements, not model access; keep no probe files."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
    for name in ("log", "crashes"):
        directory = Path.home() / ".gemini" / "antigravity-cli" / name
        directory.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=directory) as probe:
            probe.write(b"readiness check")


def diagnose_agent(agent, cwd=None):
    """Inspect participant installation, CLI version, and auth without making model calls."""
    executable = "agy" if agent == "antigravity" else agent
    cli_path = shutil.which(executable)
    if not cli_path:
        return dict(agent=agent, installed=False, authenticated=False, version=None,
                    error="CLI is not installed or not on PATH", status="missing")
    version = None
    try:
        proc = subprocess.run([executable, "--version"], stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=3)
        if proc.returncode == 0:
            version = proc.stdout.strip().splitlines()[0] if proc.stdout.strip() else None
    except Exception:
        pass

    if agent == "antigravity":
        try:
            probe_antigravity()
            return dict(agent=agent, installed=True, authenticated=True, version=version,
                        error=None, status="ok")
        except Exception as exc:
            return dict(agent=agent, installed=True, authenticated=False, version=version,
                        error=str(exc)[:200], status="error")
    else:
        args = ["claude", "auth", "status"] if agent == "claude" else ["codex", "login", "status"]
        try:
            result = subprocess.run(args, cwd=cwd, stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, timeout=10)
            if agent == "claude":
                data = json.loads(result.stdout, object_pairs_hook=unique_object)
                logged_in = isinstance(data, dict) and data.get("loggedIn") is True
            else:
                logged_in = result.returncode == 0
            if logged_in:
                return dict(agent=agent, installed=True, authenticated=True, version=version,
                            error=None, status="ok")
            else:
                return dict(agent=agent, installed=True, authenticated=False, version=version,
                            error="Authentication not visible in this execution context",
                            status="unauthenticated")
        except Exception as exc:
            return dict(agent=agent, installed=True, authenticated=False, version=version,
                        error=str(exc)[:200], status="error")


def preflight(jobs):
    """Check all participants in this execution context before any paid call."""
    jobs = validate_jobs(jobs)
    errors = []
    for job in jobs:
        agent = job["agent"]
        executable = "agy" if agent == "antigravity" else agent
        if not shutil.which(executable):
            errors.append(agent + ": CLI is not installed or not on PATH")
            continue
        try:
            if agent == "antigravity":
                probe_antigravity()
            else:
                args = ["claude", "auth", "status"] if agent == "claude" else ["codex", "login", "status"]
                result = subprocess.run(args, cwd=job["cwd"], stdin=subprocess.DEVNULL,
                                        capture_output=True, text=True, timeout=10)
                if agent == "claude":
                    data = json.loads(result.stdout, object_pairs_hook=unique_object)
                    logged_in = isinstance(data, dict) and data.get("loggedIn") is True
                else:
                    logged_in = result.returncode == 0
                if result.returncode or not logged_in:
                    raise ValueError("authentication not visible in this execution context; "
                                     "check with approved host permissions before requesting login")
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            errors.append(agent + ": " + str(exc)[:300])
    if errors:
        raise ValueError("Preflight failed; no model called. " + "; ".join(errors) +
                         ". For sandbox restrictions request host approval for this exact "
                         "command outside the sandbox; keep provider safety flags.")
    return dict(ready=True, agents=[job["agent"] for job in jobs], model_calls=0)


def command(job):
    job = validate_jobs([job])[0]
    agent, edit, prompt = job["agent"], job["access"] == "edit", job["prompt"]
    prompt = ("Do not delegate, spawn subagents, invoke other model CLIs, or start another "
              "Cogitor run. Complete this assigned task yourself.\n\n" + prompt)
    if job["context_only"]:
        prompt = ("Use only the supplied context. Do not call tools, read files, "
                  "execute commands, access external services, or delegate.\n\n" + prompt)
    if agent == "codex":
        args = ["codex", "exec", "--skip-git-repo-check", "--sandbox",
                "workspace-write" if edit else "read-only", "--json"]
        if "model" in job:
            args += ["--model", job["model"]]
        if "effort" in job:
            args += ["-c", "model_reasoning_effort=" + json.dumps(job["effort"])]
        return args + ["-"], prompt.encode("utf-8")
    options = []
    for key in ("model", "effort"):
        if key in job:
            options += ["--" + key, job[key]]
    if agent == "claude":
        args = ["claude", "--permission-mode", "acceptEdits" if edit else "plan",
                "--output-format", "json", "-p"]
        if job["context_only"]:
            args += ["--tools", "", "--strict-mcp-config", "--disable-slash-commands"]
        return args + options, prompt.encode("utf-8")
    return ["agy", "--mode", "accept-edits" if edit else "plan", "--sandbox",
            "--print-timeout", "%gs" % job["timeout_seconds"], "--output-format", "json"] + options + ["-p", prompt], None


def parse_response(agent, path):
    session, response, usage = None, None, None
    if agent == "codex":
        messages, complete = [], False
        with open(path, encoding="utf-8") as source:
            for line in source:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line, object_pairs_hook=unique_object)
                except ValueError:
                    continue
                if not isinstance(event, dict):
                    continue
                kind = event.get("type")
                if kind in ("turn.failed", "error"):
                    raise ValueError("Codex reported " + str(kind))
                if kind == "thread.started":
                    session = event.get("thread_id")
                elif kind == "item.completed":
                    item = event.get("item")
                    if isinstance(item, dict) and item.get("type") == "agent_message":
                        text = item.get("text")
                        if not isinstance(text, str):
                            raise ValueError("malformed Codex agent message")
                        messages.append(text)
                elif kind == "turn.completed":
                    complete, usage = True, event.get("usage")
        if not complete:
            raise ValueError("Codex did not provide a completed turn")
        response = "\n\n".join(messages)
    else:
        with open(path, encoding="utf-8") as source:
            data = json.load(source, object_pairs_hook=unique_object)
        if not isinstance(data, dict):
            raise ValueError("unrecognized response schema")
        if agent == "claude":
            if data.get("is_error") is not False or data.get("subtype") != "success":
                raise ValueError("Claude did not report a successful result")
            session, response = data.get("session_id"), data.get("result")
        else:
            if data.get("status") != "SUCCESS":
                raise ValueError("Antigravity did not report SUCCESS")
            session, response = data.get("conversation_id"), data.get("response")
        usage = data.get("usage")
    if usage is not None and not isinstance(usage, dict):
        raise ValueError("unrecognized usage schema")
    if not isinstance(session, str) or not session.strip() or not isinstance(response, str) or not response.strip():
        raise ValueError("response is missing text or a session ID")
    return dict(session_id=session, response=response, usage=usage)


def stop_group(process):
    # Each launcher owns a new POSIX session; never signal another job's group.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        try:
            process.terminate()
        except (ProcessLookupError, PermissionError):
            pass
    try:
        process.wait(timeout=0.3)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        try:
            process.kill()
        except (ProcessLookupError, PermissionError):
            pass
    try:
        process.wait()
    except (ProcessLookupError, PermissionError):
        pass


def private_directory(directory):
    directory = Path(directory)
    info = directory.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("results directory must be caller-owned, private, and not a symlink")
    return directory.resolve()


def private_file(path):
    return os.fdopen(os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), "wb")


def run_job(job, directory, cancelled):
    """Run one validated request, retaining logs and a normalized result."""
    job = validate_jobs([job])[0]
    directory = private_directory(directory)
    agent, process = job["agent"], None
    target_cwd = job["cwd"]
    temp_cwd = None
    if job.get("context_only"):
        temp_cwd = tempfile.mkdtemp(prefix="cogitor-iso-")
        target_cwd = temp_cwd
    start_time = time.monotonic()
    result = dict(agent=agent, status="failed", session_id=None, response=None, usage=None,
                  model=job.get("model"), effort=job.get("effort"), request_hash=fingerprint(job),
                  exit_code=None, stdout_path=str(directory / (agent + ".stdout.log")),
                  stderr_path=str(directory / (agent + ".stderr.log")),
                  result_path=str(directory / (agent + ".result.json")),
                  duration_seconds=None)
    try:
        with private_file(result["stdout_path"]) as out, private_file(result["stderr_path"]) as err:
            if cancelled.is_set():
                raise InterruptedError("run interrupted")
            args, stdin = command(job)
            process = subprocess.Popen(args, cwd=target_cwd, start_new_session=True,
                                       stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                       stdout=out, stderr=err)
            if stdin is not None:
                def feed():
                    try:
                        process.stdin.write(stdin)
                        process.stdin.close()
                    except (BrokenPipeError, OSError):
                        pass
                threading.Thread(target=feed, daemon=True).start()
            deadline = time.monotonic() + job["timeout_seconds"]
            while process.poll() is None:
                if cancelled.is_set():
                    raise InterruptedError("run interrupted")
                if time.monotonic() >= deadline:
                    raise TimeoutError("job exceeded timeout_seconds")
                if os.path.getsize(result["stdout_path"]) > MAX_OUTPUT_BYTES or os.path.getsize(result["stderr_path"]) > MAX_OUTPUT_BYTES:
                    raise ValueError("subprocess output exceeded maximum allowed size (%s bytes)" % MAX_OUTPUT_BYTES)
                time.sleep(0.01)
            if os.path.getsize(result["stdout_path"]) > MAX_OUTPUT_BYTES or os.path.getsize(result["stderr_path"]) > MAX_OUTPUT_BYTES:
                raise ValueError("subprocess output exceeded maximum allowed size (%s bytes)" % MAX_OUTPUT_BYTES)
        if process.returncode != 0:
            raise ValueError("CLI exited with code %s" % process.returncode)
        result.update(parse_response(agent, result["stdout_path"]), status="success")
    except Exception as exc:
        if process is not None and (process.poll() is None or isinstance(exc, (TimeoutError, InterruptedError))):
            stop_group(process)
        result["error"] = (type(exc).__name__ + ": " + str(exc))[:500]
        if isinstance(exc, TimeoutError):
            result["status"] = "timeout"
        elif isinstance(exc, InterruptedError):
            result["status"] = "cancelled"
    finally:
        if temp_cwd is not None:
            shutil.rmtree(temp_cwd, ignore_errors=True)
    result["exit_code"] = process.returncode if process is not None else None
    result["duration_seconds"] = round(time.monotonic() - start_time, 2)
    with private_file(result["result_path"]) as output:
        output.write((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return result


def execute_jobs(jobs, directory, cancelled=None):
    """Run 1-3 distinct providers in parallel in an empty private directory.

    The caller runs preflight before claiming a dispatch and owns cancellation;
    this API does not install signal handlers.
    Model and effort in results are requested values, never inferred values.
    """
    jobs = validate_jobs(jobs)
    directory = private_directory(directory)
    if any(directory.iterdir()):
        raise ValueError("results directory must be empty")
    if cancelled is None:
        cancelled = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = [pool.submit(run_job, job, directory, cancelled) for job in jobs]
        return [future.result() for future in futures]


def main():
    if sys.version_info < (3, 9) or os.name != "posix":
        print("requires Python 3.9+ on POSIX", file=sys.stderr)
        return 2
    try:
        check_only = len(sys.argv) == 3 and sys.argv[1] == "--check"
        if len(sys.argv) != 2 and not check_only:
            raise ValueError("usage: python3 run.py [--check] jobs.json")
        jobs = load_jobs(sys.argv[-1])
        readiness = preflight(jobs)
        if check_only:
            print(json.dumps(readiness))
            return 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2
    directory = Path(tempfile.mkdtemp(prefix="cogitor-")).resolve()
    cancelled = threading.Event()
    received_signal = 0

    def cancel(signum, _frame):
        nonlocal received_signal
        received_signal = signum
        cancelled.set()

    previous = {signum: signal.signal(signum, cancel) for signum in (signal.SIGINT, signal.SIGTERM)}
    try:
        results = execute_jobs(jobs, directory, cancelled)
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)
    keys = ("agent", "status", "session_id", "stdout_path", "stderr_path", "result_path")
    print(json.dumps({"results_dir": str(directory),
                      "jobs": [{key: result[key] for key in keys} for result in results]}))
    return 128 + received_signal if received_signal else int(any(result["status"] != "success" for result in results))


if __name__ == "__main__":
    sys.exit(main())
