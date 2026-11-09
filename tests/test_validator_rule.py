"""Unit tests for RuleValidator and RuleConflictValidator."""

import json
import sqlite3

import pytest

from src.core.models import Rule
from src.validator import RuleValidator, RuleConflictValidator


_UNSET = object()


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def create_rule():
    """Create a rule with configurable attributes."""

    def _create_rule(
        rule_type="extension",
        value=_UNSET,
        priority=2,
        parent_id=None,
        rule_id=None,
    ):
        if value is _UNSET:
            value = [".pdf"]

        return Rule(
            rule_type=rule_type,
            value=value,
            category="Test",
            priority=priority,
            parent_id=parent_id,
            rule_id=rule_id,
        )

    return _create_rule


@pytest.fixture
def valid_rule(create_rule):
    """Provide a valid rule and its validator."""

    rule = create_rule()
    return RuleValidator(rule, [1, 2, 3])


# ============================================================
# 1. RULE TYPE VALIDATION
# ============================================================

@pytest.mark.parametrize(
    "rule_type",
    ["extension", "name", "regex", "size"],
)
def test_validate_type_accepts_allowed_types(create_rule, rule_type):
    rule = create_rule(rule_type=rule_type)
    validator = RuleValidator(rule, [])

    assert validator.validate_type() is True


@pytest.mark.parametrize(
    "rule_type",
    ["unknown", "", None, 123],
)
def test_validate_type_rejects_invalid_types(create_rule, rule_type):
    rule = create_rule(rule_type=rule_type)
    validator = RuleValidator(rule, [])

    assert validator.validate_type() is False


# ============================================================
# 2. RULE VALUE VALIDATION
# ============================================================

# -------------------------
# 2.1 Extension values
# -------------------------

@pytest.mark.parametrize(
    "value",
    [
        [".pdf"],
        [".jpg", ".png"],
        [".tar.gz"],
    ],
)
def test_validate_extension_accepts_valid_values(create_rule, value):
    rule = create_rule(value=value)
    validator = RuleValidator(rule, [])

    assert validator.validate_value() is True


@pytest.mark.parametrize(
    "value",
    [
        [],
        ["pdf"],
        [""],
        [".pdf", 123],
        ".pdf",
        None,
    ],
)
def test_validate_extension_rejects_invalid_values(create_rule, value):
    rule = create_rule(value=value)
    validator = RuleValidator(rule, [])

    assert validator.validate_value() is False


# -------------------------
# 2.2 Name values
# -------------------------

@pytest.mark.parametrize(
    "value",
    [
        "report",
        "invoice 2026",
        "document.pdf",
    ],
)
def test_validate_name_accepts_valid_values(create_rule, value):
    rule = create_rule(rule_type="name", value=value)
    validator = RuleValidator(rule, [])

    assert validator.validate_value() is True


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        None,
        123,
        [],
    ],
)
def test_validate_name_rejects_invalid_values(create_rule, value):
    rule = create_rule(rule_type="name", value=value)
    validator = RuleValidator(rule, [])

    assert validator.validate_value() is False


# -------------------------
# 2.3 Regular expression values
# -------------------------

@pytest.mark.parametrize(
    "value",
    [
        r".*\.pdf$",
        r"^[a-zA-Z0-9_-]+$",
        r"\d{4}",
    ],
)
def test_validate_regex_accepts_valid_values(create_rule, value):
    rule = create_rule(rule_type="regex", value=value)
    validator = RuleValidator(rule, [])

    assert validator.validate_value() is True


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "[",
        "(",
        None,
        123,
    ],
)
def test_validate_regex_rejects_invalid_values(create_rule, value):
    rule = create_rule(rule_type="regex", value=value)
    validator = RuleValidator(rule, [])

    assert validator.validate_value() is False


# -------------------------
# 2.4 File size values
# -------------------------

@pytest.mark.parametrize(
    "value",
    [
        {"operator": ">", "amount": 500, "unit": "MB"},
        {"operator": ">=", "amount": 1.5, "unit": "GB"},
        {"operator": "==", "amount": 100, "unit": "KB"},
        {"operator": "!=", "amount": 2, "unit": "TB"},
    ],
)
def test_validate_size_accepts_valid_values(create_rule, value):
    rule = create_rule(rule_type="size", value=value)
    validator = RuleValidator(rule, [])

    assert validator.validate_value() is True


@pytest.mark.parametrize(
    "value",
    [
        {},
        {"operator": ">", "amount": 0, "unit": "MB"},
        {"operator": ">", "amount": -5, "unit": "GB"},
        {"operator": "invalid", "amount": 500, "unit": "MB"},
        {"operator": ">", "amount": "500", "unit": "MB"},
        {"operator": ">", "amount": True, "unit": "MB"},
        {"operator": ">", "amount": 500, "unit": "XB"},
        {"operator": ">", "amount": float("inf"), "unit": "MB"},
        {"operator": ">", "amount": float("nan"), "unit": "MB"},
        None,
        [],
    ],
)
def test_validate_size_rejects_invalid_values(create_rule, value):
    rule = create_rule(rule_type="size", value=value)
    validator = RuleValidator(rule, [])

    assert validator.validate_value() is False


def test_validate_value_rejects_unsupported_rule_type(create_rule):
    rule = create_rule(rule_type="unknown", value="anything")
    validator = RuleValidator(rule, [])

    assert validator.validate_value() is False


# ============================================================
# 3. PRIORITY VALIDATION
# ============================================================

@pytest.mark.parametrize("priority", [1, 2, 3, 4])
def test_validate_priority_accepts_valid_values(create_rule, priority):
    rule = create_rule(priority=priority)
    validator = RuleValidator(rule, [])

    assert validator.validate_priority() is True


@pytest.mark.parametrize(
    "priority",
    [
        0,
        5,
        -1,
        True,
        False,
        1.5,
        "2",
        None,
    ],
)
def test_validate_priority_rejects_invalid_values(create_rule, priority):
    rule = create_rule(priority=priority)
    validator = RuleValidator(rule, [])

    assert validator.validate_priority() is False


# ============================================================
# 4. PARENT ID VALIDATION
# ============================================================

def test_validate_parent_id_accepts_none(create_rule):
    rule = create_rule(parent_id=None)
    validator = RuleValidator(rule, [1, 2, 3])

    assert validator.validate_parent_id() is True


def test_validate_parent_id_accepts_existing_parent(create_rule):
    rule = create_rule(parent_id=2, rule_id=10)
    validator = RuleValidator(rule, [1, 2, 3])

    assert validator.validate_parent_id() is True


@pytest.mark.parametrize(
    "parent_id",
    [
        999,
        0,
        -1,
        True,
        False,
        1.5,
        "2",
    ],
)
def test_validate_parent_id_rejects_invalid_parent(create_rule, parent_id):
    rule = create_rule(parent_id=parent_id, rule_id=10)
    validator = RuleValidator(rule, [1, 2, 3])

    assert validator.validate_parent_id() is False


def test_validate_parent_id_rejects_self_reference(create_rule):
    rule = create_rule(parent_id=2, rule_id=2)
    validator = RuleValidator(rule, [1, 2, 3])

    assert validator.validate_parent_id() is False


# ============================================================
# 5. PARENT CYCLE VALIDATION
# ============================================================

def test_validate_parent_cycle_accepts_none(create_rule):
    """A rule without a parent cannot create a hierarchy cycle."""

    rule = create_rule(parent_id=None, rule_id=10)
    validator = RuleValidator(rule, [], {})

    assert validator.validate_parent_cycle() is True


def test_validate_parent_cycle_accepts_valid_hierarchy(create_rule):
    """A valid multi-level hierarchy must not be rejected."""

    # 1 -> None
    # 2 -> 1
    # 3 -> 2
    # 4 -> 3
    parent_relations = {
        1: None,
        2: 1,
        3: 2,
        4: 3,
    }

    rule = create_rule(parent_id=4, rule_id=10)
    validator = RuleValidator(
        rule,
        [1, 2, 3, 4],
        parent_relations,
    )

    assert validator.validate_parent_cycle() is True


def test_validate_parent_cycle_rejects_indirect_self_reference(create_rule):
    """A rule cannot become a descendant of itself."""

    # 1 -> None
    # 2 -> 1
    # 3 -> 2
    # Rule 1 attempts to use rule 3 as its parent.
    parent_relations = {
        1: None,
        2: 1,
        3: 2,
    }

    rule = create_rule(parent_id=3, rule_id=1)
    validator = RuleValidator(
        rule,
        [1, 2, 3],
        parent_relations,
    )

    assert validator.validate_parent_cycle() is False


def test_validate_parent_cycle_rejects_existing_cycle(create_rule):
    """An already circular hierarchy must be rejected."""

    # 2 -> 3 -> 2
    parent_relations = {
        2: 3,
        3: 2,
    }

    rule = create_rule(parent_id=2, rule_id=10)
    validator = RuleValidator(
        rule,
        [2, 3],
        parent_relations,
    )

    assert validator.validate_parent_cycle() is False


def test_validate_parent_cycle_rejects_missing_intermediate_reference(
    create_rule,
):
    """A missing intermediate parent reference must be rejected."""

    # Rule 3 references rule 2, but rule 2 is missing
    # from the hierarchy mapping.
    parent_relations = {
        3: 2,
    }

    rule = create_rule(parent_id=3, rule_id=10)
    validator = RuleValidator(
        rule,
        [3],
        parent_relations,
    )

    assert validator.validate_parent_cycle() is False


# ============================================================
# 6. COMPLETE RULE VALIDATION
# ============================================================

def test_validate_rule_returns_all_successful_results(valid_rule):
    results = valid_rule.validate_rule()

    assert results == {
        "type": True,
        "value": True,
        "priority": True,
        "parent_id": True,
        "parent_cycle": True,
    }


def test_validate_rule_reports_invalid_attributes(create_rule):
    rule = create_rule(
        rule_type="unknown",
        value=None,
        priority=5,
        parent_id=999,
    )

    validator = RuleValidator(rule, [1, 2, 3])

    results = validator.validate_rule()

    assert results == {
        "type": False,
        "value": False,
        "priority": False,
        "parent_id": False,
        "parent_cycle": False,
    }


# ============================================================
# 7. RULE CONFLICT VALIDATION
# ============================================================

def test_rule_conflict_validator_detects_duplicate_extension():
    """Duplicate extensions must be detected."""

    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE rules (
            id INTEGER PRIMARY KEY,
            type TEXT,
            value TEXT,
            category TEXT
        )
    """)

    connection.execute(
        "INSERT INTO rules (type, value, category) VALUES (?, ?, ?)",
        ("extension", json.dumps([".pdf"]), "Documents"),
    )

    new_rule = Rule(
        rule_type="extension",
        value=[".pdf"],
        category="Other",
        priority=2,
        parent_id=None,
    )

    validator = RuleConflictValidator(new_rule, connection)

    result = validator.validate_conflicts()

    assert result == (True, (".pdf",), "duplicate_extension")

    connection.close()


def test_rule_conflict_validator_ignores_own_rule():
    """A rule must not conflict with itself during an update."""

    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE rules (
            id INTEGER PRIMARY KEY,
            type TEXT,
            value TEXT,
            category TEXT
        )
    """)

    connection.execute(
        "INSERT INTO rules (id, type, value, category) VALUES (?, ?, ?, ?)",
        (1, "extension", json.dumps([".pdf"]), "Documents"),
    )

    new_rule = Rule(
        rule_type="extension",
        value=[".pdf"],
        category="Documents",
        priority=2,
        parent_id=None,
        rule_id=1,
    )

    validator = RuleConflictValidator(
        new_rule,
        connection,
        rule_id=1,
    )

    result = validator.validate_conflicts()

    assert result == (False, None, "success")

    connection.close()


def test_rule_conflict_validator_handles_database_error():
    """SQLite errors must return the database_error result."""

    connection = sqlite3.connect(":memory:")

    new_rule = Rule(
        rule_type="extension",
        value=[".pdf"],
        category="Documents",
        priority=2,
        parent_id=None,
    )

    validator = RuleConflictValidator(new_rule, connection)

    result = validator.validate_conflicts()

    assert result == (None, None, "database_error")

    connection.close()
