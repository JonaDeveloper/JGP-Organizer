
"""Unit tests for the rules module."""

from pathlib import Path

from src.core import rules
from src.core.models import Rule


def test_classify_file_returns_category_for_pdf():
    """Return the correct category for a PDF file."""
    test_rules = [
        Rule(
            rule_id=1,
            rule_type="extension",
            value=[".pdf"],
            category="Documents",
            priority=1,
            parent_id=None
        )
    ]

    file = Path("document.PDF")
    category, result_file = rules.classify_file(file, test_rules)

    assert category == "Documents"
    assert result_file == file


def test_classify_file_checks_all_rules():
    """Check all rules and classify a JPG file correctly."""
    test_rules = [
        Rule(
            rule_id=1,
            rule_type="extension",
            value=[".pdf"],
            category="Documents",
            priority=1,
            parent_id=None
        ),
        Rule(
            rule_id=2,
            rule_type="extension",
            value=[".jpg"],
            category="Images",
            priority=2,
            parent_id=None
        )
    ]

    file = Path("imagen.JPG")
    category, result_file = rules.classify_file(file, test_rules)

    assert category == "Images"
    assert result_file == file


def test_classify_file_returns_category_for_others():
    """Return Others when no rule matches the file extension."""
    test_rules = [
        Rule(
            rule_id=1,
            rule_type="extension",
            value=[".pdf"],
            category="Documents",
            priority=1,
            parent_id=None
        ),
        Rule(
            rule_id=2,
            rule_type="extension",
            value=[".jpg"],
            category="Images",
            priority=2,
            parent_id=None
        )
    ]

    file = Path("imagen.MP3")
    category, result_file = rules.classify_file(file, test_rules)

    assert category == "Others"
    assert result_file == file


def test_classify_file_respects_priority():
    """The rule with the lowest priority number should win."""
    test_rules = [
        Rule(
            rule_id=1,
            rule_type="extension",
            value=[".pdf"],
            category="Documents",
            priority=2,
            parent_id=None
        ),
        Rule(
            rule_id=2,
            rule_type="extension",
            value=[".pdf"],
            category="Important Documents",
            priority=1,
            parent_id=None
        )
    ]

    file = Path("document.pdf")
    category, result_file = rules.classify_file(file, test_rules)

    assert category == "Important Documents"
    assert result_file == file
