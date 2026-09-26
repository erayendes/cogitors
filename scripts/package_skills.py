#!/usr/bin/env python3
"""Build four portable skill folders and .skill ZIPs with Python 3.9+."""

import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile
import zipfile


NAMES = ("cogitors", "codex", "claude", "antigravity")
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9-]{1,64}$")
EXTENSIONS = {".md", ".py", ".yaml"}
SHARED = ("scripts/run.py", "references/execution.md")
SENSITIVE_NAME = re.compile(
    r"(?:^|[._-])(?:auth|credentials?|secrets?|tokens?|passwords?)(?:[._-]|$)", re.I
)
# ponytail: these recognizable credential signatures are not a full secret audit.
SECRET_CONTENT = re.compile(
    rb"-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----|"
    rb"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b"
)


def collect(folder):
    """Read an allowlisted tree before creating any output."""
    if folder.is_symlink() or not folder.is_dir():
        raise ValueError("Expected a real skill directory: {}".format(folder))
    files = {}
    for path in sorted(folder.rglob("*")):
        relative = path.relative_to(folder)
        if path.is_symlink():
            raise ValueError("Symlinks are not allowed: {}".format(path))
        if path.name == ".DS_Store" and path.is_file():
            continue
        if any(part == "__pycache__" for part in relative.parts) or path.suffix == ".pyc":
            continue
        if any(part.startswith(".") or part in {"node_modules", "cache"}
               or SENSITIVE_NAME.search(part) for part in relative.parts):
            raise ValueError("Hidden, cached, or sensitive entry: {}".format(path))
        if path.is_dir():
            continue
        if not path.is_file() or path.suffix not in EXTENSIONS:
            raise ValueError("Unsupported source file: {}".format(path))
        content = path.read_bytes()
        if SECRET_CONTENT.search(content):
            raise ValueError("Possible credential in source file: {}".format(path))
        files[relative.as_posix()] = content
    return files


def validate_skill(name, files):
    if not SKILL_NAME_PATTERN.match(name):
        raise ValueError("Invalid skill name format: {}".format(name))
    if "SKILL.md" not in files:
        raise ValueError("{} is missing SKILL.md".format(name))
    lines = files["SKILL.md"].decode("utf-8").splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError("{} needs YAML frontmatter delimited by ---".format(name))
    frontmatter = lines[1:lines.index("---", 1)]
    names = [line[5:].strip().strip("\"'") for line in frontmatter if line.startswith("name:")]
    if names != [name]:
        raise ValueError("{} frontmatter must contain exactly name: {}".format(name, name))
    descriptions = [line[12:].strip() for line in frontmatter if line.startswith("description:")]
    if not descriptions or not descriptions[0]:
        raise ValueError("{} frontmatter needs a description".format(name))
    if len(descriptions[0]) > 1024:
        raise ValueError("{} description must be <= 1024 characters".format(name))


def package(source, output):
    if source.is_symlink() or (source / "skills").is_symlink():
        raise ValueError("Source directories must not be symlinks")
    if output.is_symlink():
        raise ValueError("Output must not be a symlink")
    source, output = source.resolve(), output.resolve()
    if output == source or output.is_relative_to(source / "skills"):
        raise ValueError("Output must be outside the skill source folders")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("Output must be a new or empty directory: {}".format(output))
    bundles = {}
    for name in NAMES:
        bundles[name] = collect(source / "skills" / name)
        validate_skill(name, bundles[name])
    for relative in SHARED:
        if relative not in bundles["cogitors"]:
            raise ValueError("cogitors is missing {}".format(relative))
        for name in NAMES[1:]:
            if relative in bundles[name]:
                raise ValueError("{} must use the shared {}".format(name, relative))
            bundles[name][relative] = bundles["cogitors"][relative]

    output_parent = output.parent if output.parent.exists() else output
    output_parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".cogitors-pkg-", dir=output_parent)).resolve()
    try:
        summary = {"folders": [], "archives": []}
        for name, files in bundles.items():
            folder, archive = staging / name, staging / (name + ".skill")
            folder.mkdir()
            with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as bundle:
                for relative, content in sorted(files.items()):
                    target = folder / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
                    info = zipfile.ZipInfo(name + "/" + relative, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = (0o755 if (relative.endswith(".py") or relative.endswith(".sh")) else 0o644) << 16
                    bundle.writestr(info, content)
            summary["folders"].append(str(output / name))
            summary["archives"].append(str(output / (name + ".skill")))
        if output.exists():
            output.rmdir()
        staging.replace(output)
        return summary
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1],
                        help="Repository root (default: this script's repository)")
    parser.add_argument("--output", type=Path, default=Path("dist"),
                        help="New or empty output directory (default: ./dist)")
    args = parser.parse_args()
    try:
        summary = package(args.source, args.output)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
