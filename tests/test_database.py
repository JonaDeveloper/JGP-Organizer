
"""Tests for database rule operations."""

import sqlite3

import pytest

from src.db.database import (
    initialize_rules_database,
    insert_rule,
    update_rule,
    delete_rule,
)
from src.core.models import Rule


@pytest.fixture
def test_db(tmp_path):
    """Create an isolated temporary database for each test."""
    db_path = tmp_path / "test_database.db"
    initialize_rules_database(str(db_path))
    return str(db_path)


def create_rule(extension, category="Test", priority=2):
    """Create a custom extension rule for testing."""
    return Rule(
        rule_type="extension",
        value=[extension],
        category=category,
        priority=priority,
        parent_id=None,
    )


def get_default_rule_id(db_path):
    """Retrieve the ID of a default rule from the database."""
    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            "SELECT id FROM rules WHERE is_default = 1 LIMIT 1"
        ).fetchone()

    assert result is not None, "The database must contain a default rule."
    return result[0]


# -------------------------
# INSERT RULE TESTS
# -------------------------

def test_insert_rule_success(test_db):
    """A valid custom rule should be inserted successfully."""
    rule = create_rule(".jgp_insert_success")

    result = insert_rule(rule, db_path=test_db)

    assert result == (True, None, "success")
    assert rule.rule_id is not None


def test_insert_duplicate_extension(test_db):
    """An extension already registered should be rejected."""
    first_rule = create_rule(".jgp_duplicate")

    first_result = insert_rule(first_rule, db_path=test_db)

    assert first_result == (True, None, "success")

    duplicate_rule = create_rule(".jgp_duplicate")

    result = insert_rule(duplicate_rule, db_path=test_db)

    assert result[0] is False
    assert result[2] == "duplicate_extension"
    assert ".jgp_duplicate" in result[1]


def test_insert_rule_limit(test_db):
    """The database should reject custom rules after the limit is reached."""
    for number in range(5):
        rule = create_rule(
            extension=f".jgp_limit{number}",
            priority=number + 2,
        )

        result = insert_rule(rule, db_path=test_db)

        assert result == (True, None, "success")

    extra_rule = create_rule(".jgp_limit_extra", priority=10)

    result = insert_rule(extra_rule, db_path=test_db)

    assert result == (False, None, "rule_limit_reached")


# -------------------------
# UPDATE RULE TESTS
# -------------------------

def test_update_rule_success(test_db):
    """An existing custom rule should be updated successfully."""
    rule = create_rule(".jgp_before_update")

    insert_result = insert_rule(rule, db_path=test_db)
    assert insert_result == (True, None, "success")

    rule.value = [".jgp_after_update"]
    rule.category = "Updated"
    rule.priority = 5

    result = update_rule(rule, db_path=test_db)

    assert result == (True, None, "success")

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT value, category, priority FROM rules WHERE id = ?",
            (rule.rule_id,),
        ).fetchone()

    assert row is not None
    assert row[0] == '[".jgp_after_update"]'
    assert row[1] == "Updated"
    assert row[2] == 5


def test_update_rule_nonexistent(test_db):
    """A nonexistent rule should not be updated."""
    rule = create_rule(".jgp_missing_update")
    rule.id = 999999

    result = update_rule(rule, db_path=test_db)

    assert result == (False, None, "invalid_rule")


def test_update_default_rule(test_db):
    """A default rule should not be updated."""
    rule_id = get_default_rule_id(test_db)

    rule = Rule(
        rule_type="extension",
        value=[".jgp_default_update"],
        category="Updated",
        priority=5,
        parent_id=None,
        rule_id=rule_id,
    )

    result = update_rule(rule, db_path=test_db)

    assert result == (False, None, "invalid_rule")


def test_update_rule_duplicate_extension(test_db):
    """Updating a rule to use another rule's extension should fail."""
    first_rule = create_rule(".jgp_update_conflict_a")
    second_rule = create_rule(".jgp_update_conflict_b")

    assert insert_rule(first_rule, db_path=test_db)[0] is True
    assert insert_rule(second_rule, db_path=test_db)[0] is True

    second_rule.value = [".jgp_update_conflict_a"]

    result = update_rule(second_rule, db_path=test_db)

    assert result[0] is False
    assert result[2] == "duplicate_extension"


# -------------------------
# DELETE RULE TESTS
# -------------------------

def test_delete_rule_success(test_db):
    """An existing custom rule should be deleted successfully."""
    rule = create_rule(".jgp_delete_success")

    insert_result = insert_rule(rule, db_path=test_db)
    assert insert_result == (True, None, "success")

    result = delete_rule(rule.rule_id, db_path=test_db)

    assert result == (True, None, "success")

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT id FROM rules WHERE id = ?",
            (rule.rule_id,),
        ).fetchone()

    assert row is None


def test_delete_rule_nonexistent(test_db):
    """A nonexistent rule should not be deleted."""
    result = delete_rule(999999, db_path=test_db)

    assert result == (False, None, "invalid_rule")


def test_delete_default_rule(test_db):
    """A default rule should not be deleted."""
    rule_id = get_default_rule_id(test_db)

    result = delete_rule(rule_id, db_path=test_db)

    assert result == (False, None, "invalid_rule")

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT id FROM rules WHERE id = ? AND is_default = 1",
            (rule_id,),
        ).fetchone()

    assert row is not None
