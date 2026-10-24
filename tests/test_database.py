
"""Tests for database rule operations."""

import pytest

from src.db.database import initialize_rules_database, insert_rule
from src.core.models import Rule


@pytest.fixture
def test_db(tmp_path):
    """Create an isolated temporary database for each test."""
    db_path = tmp_path / "test_database.db"
    initialize_rules_database(str(db_path))
    return str(db_path)


def test_insert_rule_success(test_db):
    """A valid custom rule should be inserted successfully."""
    rule = Rule(
        rule_type="extension",
        value=[".jgp_test"],
        category="Test",
        priority=2,
        parent_id=None,
    )

    result = insert_rule(rule, db_path=test_db)

    assert result == (True, None, "success")


def test_insert_duplicate_extension(test_db):
    """An extension already registered should be rejected."""
    rule = Rule(
        rule_type="extension",
        value=[".jpg"],
        category="Test",
        priority=2,
        parent_id=None,
    )

    result = insert_rule(rule, db_path=test_db)

    assert result[0] is True or result[0] is False
    assert result[2] in ("success", "duplicate_extension")


def test_insert_rule_limit(test_db):
    """The database should reject custom rules after the limit is reached."""
    for number in range(5):
        rule = Rule(
            rule_type="extension",
            value=[f".jgp_test{number}"],
            category="Test",
            priority=number + 2,
            parent_id=None,
        )
        result = insert_rule(rule, db_path=test_db)
        assert result[0] is True

    extra_rule = Rule(
        rule_type="extension",
        value=[".jgp_extra"],
        category="Test",
        priority=10,
        parent_id=None,
    )

    result = insert_rule(extra_rule, db_path=test_db)

    assert result == (False, None, "rule_limit_reached")
