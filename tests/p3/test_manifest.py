"""Tests for manifest validation and generation."""

from __future__ import annotations

from pathlib import Path

from contracts import SourceManifestEntry, SourceType
from scripts.p3.manifest import build_manifest_entries, validate_manifest, write_manifest


def test_real_manifest_is_valid() -> None:
    """The real data/manifest.json in the repository must be 100% valid."""
    manifest_path = Path("data/manifest.json")
    assert manifest_path.exists(), "data/manifest.json must exist"
    errors = validate_manifest(manifest_path)
    assert errors == [], f"Validation errors found: {errors}"


def test_build_manifest_entries_finds_all_docs() -> None:
    """build_manifest_entries must index all 18 markdown documents."""
    entries = build_manifest_entries(Path("data"))
    assert len(entries) == 18
    source_ids = {e.source_id for e in entries}
    assert "SRC-ALPHA-001" in source_ids
    assert "SRC-NOVA-001" in source_ids
    assert "SRC-DELTA-003" in source_ids


def test_validate_manifest_detects_duplicate_id(tmp_path: Path) -> None:
    """Validator must detect duplicate source_id entries."""
    entry1 = SourceManifestEntry(
        source_id="SRC-ALPHA-001",
        project_id="alpha",
        source_type=SourceType.adr,
        title="Doc 1",
        file_path="historical/alpha/SRC-ALPHA-001_messaging_architecture.md",
        date="2024-01-01T00:00:00",
    )
    entry2 = SourceManifestEntry(
        source_id="SRC-ALPHA-001",  # duplicate
        project_id="alpha",
        source_type=SourceType.adr,
        title="Doc 2",
        file_path="historical/alpha/SRC-ALPHA-001_messaging_architecture.md",
        date="2024-01-02T00:00:00",
    )
    p = tmp_path / "manifest.json"
    write_manifest([entry1, entry2], p)
    errors = validate_manifest(p)
    assert any("duplicate source_id" in err for err in errors)


def test_validate_manifest_detects_bad_format(tmp_path: Path) -> None:
    """Validator must detect malformed source_id values."""
    entry = SourceManifestEntry(
        source_id="INVALID-ID",
        project_id="alpha",
        source_type=SourceType.adr,
        title="Bad Doc",
        file_path="historical/alpha/SRC-ALPHA-001_messaging_architecture.md",
        date="2024-01-01T00:00:00",
    )
    p = tmp_path / "manifest.json"
    write_manifest([entry], p)
    errors = validate_manifest(p)
    assert any("bad source_id format" in err for err in errors)


def test_validate_manifest_detects_project_mismatch(tmp_path: Path) -> None:
    """Validator must detect when source_id project doesn't match project_id."""
    entry = SourceManifestEntry(
        source_id="SRC-ALPHA-001",
        project_id="beta",  # mismatch
        source_type=SourceType.adr,
        title="Mismatch Doc",
        file_path="historical/alpha/SRC-ALPHA-001_messaging_architecture.md",
        date="2024-01-01T00:00:00",
    )
    p = tmp_path / "manifest.json"
    write_manifest([entry], p)
    errors = validate_manifest(p)
    assert any("project" in err.lower() and "!=" in err for err in errors)


def test_validate_manifest_detects_missing_file(tmp_path: Path) -> None:
    """Validator must detect when referenced file does not exist on disk."""
    entry = SourceManifestEntry(
        source_id="SRC-ALPHA-999",
        project_id="alpha",
        source_type=SourceType.adr,
        title="Missing Doc",
        file_path="nonexistent/file.md",
        date="2024-01-01T00:00:00",
    )
    p = tmp_path / "manifest.json"
    write_manifest([entry], p)
    errors = validate_manifest(p)
    assert any("file not found" in err for err in errors)
