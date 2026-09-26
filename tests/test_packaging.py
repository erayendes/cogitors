"""Offline checks for the four self-contained skill bundles."""

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


PACKAGER = Path(__file__).resolve().parents[1] / "scripts" / "package_skills.py"
NAMES = ("cogitors", "codex", "claude", "antigravity")
RUNNER = (
    "import argparse\n"
    "argparse.ArgumentParser(description='portable fixture runner').parse_args()\n"
)


class PackagingTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "source"
        self.output = self.root / "bundles"
        for name in NAMES:
            folder = self.source / "skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text(
                "---\nname: {}\ndescription: Offline fixture.\n---\n"
                "See [execution](references/execution.md).\n".format(name),
                encoding="utf-8",
            )
        cogitors = self.source / "skills" / "cogitors"
        (cogitors / "scripts").mkdir()
        (cogitors / "scripts" / "run.py").write_text(RUNNER, encoding="utf-8")
        (cogitors / "references").mkdir()
        (cogitors / "references" / "execution.md").write_text(
            "Portable execution instructions.\n", encoding="utf-8"
        )

    def run_packager(self):
        return subprocess.run(
            [sys.executable, str(PACKAGER), "--source", str(self.source),
             "--output", str(self.output)],
            capture_output=True, text=True, check=False,
        )

    def assert_rejected(self):
        result = self.run_packager()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("error:", result.stderr)
        self.assertFalse(self.output.exists(), "Preflight must leave no partial output")

    def test_archives_and_folders_are_self_contained(self):
        support = self.source / "skills" / "claude" / "references"
        support.mkdir()
        (support / "notes.md").write_text("Own support file.\n", encoding="utf-8")
        (support / "settings.yaml").write_text("mode: local\n", encoding="utf-8")
        self.output.mkdir()  # An existing empty output directory is valid.
        result = self.run_packager()
        self.assertEqual(result.returncode, 0, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(len(summary["folders"]), 4)
        self.assertEqual(len(summary["archives"]), 4)
        for name in NAMES:
            folder = self.output / name
            self.assertEqual((folder / "scripts" / "run.py").read_text(), RUNNER)
            self.assertEqual(
                (folder / "references" / "execution.md").read_bytes(),
                (self.source / "skills" / "cogitors" / "references" / "execution.md").read_bytes(),
            )
            with zipfile.ZipFile(self.output / (name + ".skill")) as archive:
                self.assertIsNone(archive.testzip())
                expected = {
                    name + "/" + path.relative_to(folder).as_posix()
                    for path in folder.rglob("*") if path.is_file()
                }
                self.assertEqual(set(archive.namelist()), expected)
                for member in archive.namelist():
                    self.assertEqual(archive.read(member), (self.output / member).read_bytes())
                extracted = self.root / "extracted" / name
                archive.extractall(extracted)
            help_result = subprocess.run(
                [sys.executable, str(extracted / name / "scripts" / "run.py"), "--help"],
                cwd=self.root, capture_output=True, text=True, check=False,
            )
            self.assertEqual(help_result.returncode, 0, help_result.stderr)
            self.assertIn("portable fixture runner", help_result.stdout)
        self.assertEqual(
            (self.output / "claude" / "references" / "notes.md").read_bytes(),
            (support / "notes.md").read_bytes(),
        )

    def test_missing_required_files_leave_no_output(self):
        execution = self.source / "skills" / "cogitors" / "references" / "execution.md"
        execution.unlink()
        self.assert_rejected()

    def test_finder_metadata_is_ignored_not_packaged(self):
        metadata = self.source / "skills" / "cogitors" / ".DS_Store"
        metadata.write_bytes(b"Finder metadata")
        result = self.run_packager()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(metadata.exists())
        with zipfile.ZipFile(self.output / "cogitors.skill") as archive:
            self.assertFalse(any(".DS_Store" in name for name in archive.namelist()))

    def test_invalid_skill_frontmatter_leaves_no_output(self):
        skill = self.source / "skills" / "codex" / "SKILL.md"
        for contents in ("No frontmatter\n", "---\nname: wrong\n---\n", "---\nname: codex\n"):
            with self.subTest(contents=contents):
                skill.write_text(contents, encoding="utf-8")
                self.assert_rejected()

    def test_unsafe_entries_are_rejected(self):
        folder = self.source / "skills" / "codex"
        for relative in (".env", "credentials.yaml", "auth.yaml", "secrets.md",
                         ".hidden/readme.md", "notes.txt"):
            with self.subTest(relative=relative):
                path = folder / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("must not ship\n", encoding="utf-8")
                self.assert_rejected()
                path.unlink()
                if path.parent != folder:
                    path.parent.rmdir()

    def test_pycache_and_pyc_are_ignored_not_packaged(self):
        folder = self.source / "skills" / "codex"
        pycache = folder / "__pycache__"
        pycache.mkdir(parents=True, exist_ok=True)
        (pycache / "run.cpython-311.pyc").write_bytes(b"compiled python bytecode")
        (folder / "extra.pyc").write_bytes(b"stray pyc")
        result = self.run_packager()
        self.assertEqual(result.returncode, 0, result.stderr)
        with zipfile.ZipFile(self.output / "codex.skill") as archive:
            self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in archive.namelist()))
        self.assertFalse((self.output / "codex" / "__pycache__").exists())

    def test_invalid_skill_name_or_long_description_rejected(self):
        skill = self.source / "skills" / "codex" / "SKILL.md"
        skill.write_text("---\nname: codex\ndescription: " + ("a" * 1025) + "\n---\n", encoding="utf-8")
        self.assert_rejected()

    def test_symlink_and_injection_collision_are_rejected(self):
        folder = self.source / "skills" / "codex"
        link = folder / "linked.md"
        link.symlink_to(self.source / "skills" / "cogitors" / "SKILL.md")
        self.assert_rejected()
        link.unlink()
        (folder / "scripts").mkdir()
        (folder / "scripts" / "run.py").write_text("raise RuntimeError('duplicate')\n")
        self.assert_rejected()

    def test_nonempty_output_is_preserved(self):
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("existing user file\n", encoding="utf-8")
        result = self.run_packager()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error:", result.stderr)
        self.assertEqual(sentinel.read_text(), "existing user file\n")
        self.assertEqual(list(self.output.iterdir()), [sentinel])


if __name__ == "__main__":
    unittest.main()
