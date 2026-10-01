"""Bounded, read-only artifact and Git inspection shared by operator tools."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess

from schema_validation import validate_instance

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "docs/agent/schemas"
MAX_BYTES = 4 * 1024 * 1024
STAGES = ["prepare", "brainstorm", "plan", "analyze", "red_test", "green_code", "refactor", "quality_gate", "converge"]


def relative_path(value: str) -> bool:
    """Only literal repository-relative files/directories, never globs or traversal."""
    return bool(value and value != "." and not PurePosixPath(value).is_absolute()
                and all(part not in {"", ".", "..", ".git"} for part in value.split("/"))
                and not any(c in value for c in "\\:*?[]\x00\r\n"))


def contained(root: Path, name: str) -> Path:
    if not relative_path(name):
        raise ValueError(f"Unsafe relative path: {name!r}")
    root = root.resolve()
    path = root / name
    if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root and p.is_relative_to(root)):
        raise ValueError(f"Symlinks are not supported: {name}")
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"Path escapes selected directory: {name}")
    return path


def read_bytes(root: Path, name: str) -> bytes:
    path = contained(root, name)
    if not path.is_file():
        raise ValueError(f"Missing file: {name}")
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError(f"File exceeds {MAX_BYTES} byte inspection limit: {name}")
    return data


def read_json(root: Path, name: str, schema: str | None = None) -> dict:
    try:
        document = json.loads(read_bytes(root, name))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid JSON: {name}: {exc}") from exc
    if not isinstance(document, dict):
        raise ValueError(f"Expected JSON object: {name}")
    if schema:
        errors = validate_instance(document, json.loads((SCHEMAS / schema).read_text()))
        if errors:
            raise ValueError(f"{name}: " + "; ".join(errors[:10]))
    return document


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(["git", "-c", "core.fsmonitor=false", "-C", str(repo), *args], capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"Git inspection failed: {exc}") from exc
    if result.returncode:
        raise ValueError("Git inspection failed: " + result.stderr.decode("utf-8", "replace").strip())
    if len(result.stdout) > MAX_BYTES:
        raise ValueError("Git response exceeds inspection budget")
    return result.stdout


def repository_root(repo: Path) -> Path:
    selected = repo.resolve()
    actual = Path(git(selected, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if selected != actual:
        raise ValueError("Select the repository root, not a subdirectory")
    return actual


def save_new(path: Path, content: str) -> None:
    """Reports and scaffolds cannot silently replace evidence or existing files."""
    if path.is_symlink():
        raise ValueError(f"Refusing symlink output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(content)
    except FileExistsError as exc:
        raise ValueError(f"Output already exists; choose a new path: {path}") from exc


def json_text(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def finding(code: str, message: str, refs: list[str], severity: str = "blocking") -> dict:
    return {"code": code, "severity": severity, "message": message, "artifact_refs": refs}


def report(kind: str, story: str, fingerprints: dict[str, str], findings: list[dict]) -> dict:
    return {"schema_version": "1.0", "kind": kind, "story_id": story,
            "authority": "advisory", "input_sha256": fingerprints,
            "status": "blocked" if any(f["severity"] == "blocking" for f in findings) else "review" if findings else "clear",
            "findings": findings}
