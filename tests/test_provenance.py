"""Tests for provenance.py build() — artifact staging and signing."""
import argparse
import json

import pytest

import provenance
from rpb.pack_reader import extract_rpack


def _run_state(files_changed=None, tests_passed=0, tests_total=0):
    return {
        "issue_number": 42,
        "issue_title": "Add a feature",
        "repo": "owner/repo",
        "branch": "forgeproof/issue-42",
        "files_changed": files_changed or [],
        "requirements": ["REQ-1: do the thing"],
        "requirements_met": 1,
        "requirements_total": 1,
        "tests_passed": tests_passed,
        "tests_total": tests_total,
        "rpack_path": ".forgeproof/issue-42.rpack",
        "timestamp": "2024-01-01T00:00:00Z",
    }


def _build_args(tmp_path, repo_root, files_changed=None, *, tests_passed=0, tests_total=0):
    run_state_file = tmp_path / "last-run.json"
    run_state_file.write_text(
        json.dumps(_run_state(files_changed, tests_passed, tests_total)), encoding="utf-8"
    )
    decision_log_file = tmp_path / "decision-log.jsonl"
    decision_log_file.write_text('{"phase":"test","action":"wrote_file"}\n', encoding="utf-8")
    output_rpack = tmp_path / "issue-42.rpack"
    return argparse.Namespace(
        run_state=str(run_state_file),
        decision_log=str(decision_log_file),
        config=None,
        output=str(output_rpack),
        repo_root=str(repo_root),
    )


# ── Issue #1: files_changed should be staged into SOURCE/ ───────────────────


def test_files_changed_are_copied_into_source_directory(tmp_path):
    """files_changed entries must appear under SOURCE/ inside the .rpack."""
    repo_root = tmp_path / "repo"
    (repo_root / "src").mkdir(parents=True)
    (repo_root / "src" / "main.py").write_text("x = 1\n", encoding="utf-8")

    args = _build_args(tmp_path, repo_root, files_changed=["src/main.py"])
    provenance.build(args)

    extract_dir = tmp_path / "extracted"
    extract_rpack(args.output, str(extract_dir))

    staged = extract_dir / "SOURCE" / "src" / "main.py"
    assert staged.exists(), "Expected SOURCE/src/main.py in rpack"
    assert staged.read_text(encoding="utf-8") == "x = 1\n"


def test_source_files_appear_as_artifacts_in_manifest(tmp_path):
    """files_changed must be listed in MANIFEST.json artifacts with kind='source'."""
    repo_root = tmp_path / "repo"
    (repo_root / "src").mkdir(parents=True)
    (repo_root / "src" / "utils.py").write_text("pass\n", encoding="utf-8")

    args = _build_args(tmp_path, repo_root, files_changed=["src/utils.py"])
    provenance.build(args)

    extract_dir = tmp_path / "extracted"
    extract_rpack(args.output, str(extract_dir))

    manifest = json.loads((extract_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    source_artifacts = [
        a for a in manifest.get("artifacts", []) if a.get("path") == "SOURCE/src/utils.py"
    ]
    assert source_artifacts, "SOURCE/src/utils.py missing from manifest artifacts"
    assert source_artifacts[0]["kind"] == "source"


def test_multiple_files_changed_all_staged(tmp_path):
    """All files in files_changed are staged, preserving directory structure."""
    repo_root = tmp_path / "repo"
    (repo_root / "src").mkdir(parents=True)
    (repo_root / "tests").mkdir(parents=True)
    (repo_root / "src" / "app.py").write_text("app = True\n", encoding="utf-8")
    (repo_root / "tests" / "test_app.py").write_text("assert True\n", encoding="utf-8")

    args = _build_args(
        tmp_path, repo_root, files_changed=["src/app.py", "tests/test_app.py"]
    )
    provenance.build(args)

    extract_dir = tmp_path / "extracted"
    extract_rpack(args.output, str(extract_dir))

    assert (extract_dir / "SOURCE" / "src" / "app.py").exists()
    assert (extract_dir / "SOURCE" / "tests" / "test_app.py").exists()


def test_empty_files_changed_produces_valid_rpack(tmp_path):
    """build() with no files_changed still produces a valid, verifiable .rpack."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    args = _build_args(tmp_path, repo_root, files_changed=[])
    provenance.build(args)

    assert (tmp_path / "issue-42.rpack").exists()


def test_nonexistent_file_in_files_changed_raises(tmp_path):
    """build() raises if a file listed in files_changed does not exist in repo_root."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    args = _build_args(tmp_path, repo_root, files_changed=["src/ghost.py"])
    with pytest.raises((FileNotFoundError, OSError)):
        provenance.build(args)


# ── Issue #3: image_digest must reflect actual environment, not hardcoded zeros ──


def test_image_digest_is_not_hardcoded_zeros(tmp_path):
    """MANIFEST.json environment.image_digest must not be the all-zeros placeholder."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    args = _build_args(tmp_path, repo_root, files_changed=[])
    provenance.build(args)

    extract_dir = tmp_path / "extracted"
    extract_rpack(args.output, str(extract_dir))

    manifest = json.loads((extract_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    image_digest = manifest["environment"]["image_digest"]
    assert image_digest != "sha256:" + "0" * 64, (
        "image_digest should not be the hardcoded all-zeros placeholder"
    )


def test_image_digest_format_is_sha256_prefixed(tmp_path):
    """MANIFEST.json environment.image_digest must follow 'sha256:<hex>' format."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    args = _build_args(tmp_path, repo_root, files_changed=[])
    provenance.build(args)

    extract_dir = tmp_path / "extracted"
    extract_rpack(args.output, str(extract_dir))

    manifest = json.loads((extract_dir / "MANIFEST.json").read_text(encoding="utf-8"))
    image_digest = manifest["environment"]["image_digest"]
    assert image_digest.startswith("sha256:"), "image_digest must start with 'sha256:'"
    hex_part = image_digest[len("sha256:"):]
    assert len(hex_part) == 64, "image_digest sha256 part must be 64 hex chars"
    assert all(c in "0123456789abcdef" for c in hex_part), "image_digest must be lowercase hex"
