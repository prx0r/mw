"""Harbor verifier for technical ideation outputs."""
import re
from pathlib import Path


def test_output_exists(output_dir: Path):
    output_file = output_dir / "submission.md"
    assert output_file.exists(), "submission.md not found"


def test_minimum_length(output_dir: Path):
    content = (output_dir / "submission.md").read_text()
    assert len(content) > 200, f"Output too short: {len(content)} chars"


def test_has_structure(output_dir: Path):
    content = (output_dir / "submission.md").read_text()
    has_headers = bool(re.search(r'#{1,3}\s', content))
    has_lists = bool(re.search(r'^[-*]\s', content, re.MULTILINE))
    assert has_headers or has_lists, "Output lacks structure"


def test_addresses_requirements(output_dir: Path):
    content = (output_dir / "submission.md").read_text().lower()
    key_terms = ["architecture", "technical", "implementation", "innovation", "api"]
    found = sum(1 for t in key_terms if t in content)
    assert found >= 3, f"Only found {found}/5 key terms"


def test_has_code_reference(output_dir: Path):
    content = (output_dir / "submission.md").read_text()
    has_code = "```" in content or "0x" in content or "v1" in content
    assert has_code, "Output lacks specific technical references"
