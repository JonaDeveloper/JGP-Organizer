"""Integration tests for database rule operations."""

import sqlite3

import pytest

from src.db.database import (
    initialize_rules_database,
    insert_rule,
    update_rule,
    delete_rule,
)
from src.core.models import Rule


# ============================================================
# FIXTURES AND HELPERS
# ============================================================

@pytest.fixture
def test_db(tmp_path):
    """Create an isolated temporary database for each test."""
    db_path = tmp_path / "test_database.db"
    initialize_rules_database(str(db_path))
    return str(db_path)


def create_rule(extension, category="Test", priority=2, parent_id=None):
    """Create a custom extension rule with configurable hierarchy."""
    return Rule(
        rule_type="extension",
        value=[extension],
        category=category,
        priority=priority,
        parent_id=parent_id,
    )


def get_default_rule_id(db_path):
    """Retrieve the ID of a default rule from the database."""
    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            "SELECT id FROM rules WHERE is_default = 1 LIMIT 1"
        ).fetchone()

    assert result is not None, "The database must contain a default rule."
    return result[0]


def get_rule_data(db_path, rule_id):
    """Retrieve a complete rule row for persistence assertions."""
    with sqlite3.connect(db_path) as conn:
        return conn.execute(
            "SELECT * FROM rules WHERE id = ?",
            (rule_id,),
        ).fetchone()


# ============================================================
# 1. INSERT RULE TESTS
# ============================================================

# -------------------------
# 1.1 Successful insertion
# -------------------------

def test_insert_rule_success(test_db):
    """A valid custom rule should be inserted successfully."""
    rule = create_rule(".jgp_insert_success")

    result = insert_rule(rule, db_path=test_db)

    assert result == (True, None, "success")
    assert rule.rule_id is not None


def test_insert_rule_with_valid_multi_level_hierarchy(test_db):
    """A new rule may be attached to an existing multi-level hierarchy."""
    root = create_rule(".jgp_hierarchy_root")
    assert insert_rule(root, test_db) == (True, None, "success")

    middle = create_rule(".jgp_hierarchy_middle", parent_id=root.rule_id)
    assert insert_rule(middle, test_db) == (True, None, "success")

    leaf = create_rule(".jgp_hierarchy_leaf", parent_id=middle.rule_id)
    result = insert_rule(leaf, test_db)

    assert result == (True, None, "success")
    assert get_rule_data(test_db, leaf.rule_id)[5] == middle.rule_id


def test_insert_rule_rejects_parent_with_existing_cycle(test_db):
    """Insertion must be rejected if the selected parent belongs to a cycle."""
    first = create_rule(".jgp_cycle_first")
    second = create_rule(".jgp_cycle_second")

    assert insert_rule(first, test_db) == (True, None, "success")
    assert insert_rule(second, test_db) == (True, None, "success")

    # Deliberately corrupt the stored hierarchy to simulate inconsistent data:
    # first -> second -> first.
    with sqlite3.connect(test_db) as conn:
        conn.execute(
            "UPDATE rules SET parent_id = ? WHERE id = ?",
            (second.rule_id, first.rule_id),
        )
        conn.execute(
            "UPDATE rules SET parent_id = ? WHERE id = ?",
            (first.rule_id, second.rule_id),
        )

    new_rule = create_rule(".jgp_cycle_new", parent_id=first.rule_id)
    result = insert_rule(new_rule, test_db)

    assert result == (False, None, "invalid_rule")
    assert get_rule_data(test_db, new_rule.rule_id) is None


# -------------------------
# 1.2 Duplicate extension
# -------------------------

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


# -------------------------
# 1.3 Custom rule limit
# -------------------------

def test_insert_rule_limit(test_db):
    """The database should reject custom rules after the limit is reached."""
    for number in range(5):
        rule = create_rule(extension=f".jgp_limit{number}")
        result = insert_rule(rule, db_path=test_db)
        assert result == (True, None, "success")

    extra_rule = create_rule(".jgp_limit_extra")
    result = insert_rule(extra_rule, db_path=test_db)

    assert result == (False, None, "rule_limit_reached")


# -------------------------
# 1.4 Invalid insertion data
# -------------------------

@pytest.mark.parametrize(
    "rule",
    [
        create_rule(".invalid", priority=5),
        Rule(
            rule_type="extension",
            value=["pdf"],
            category="Test",
            priority=2,
            parent_id=None,
        ),
        Rule(
            rule_type="extension",
            value=[".invalid"],
            category="Test",
            priority=2,
            parent_id=999999,
        ),
    ],
    ids=[
        "invalid_priority",
        "invalid_extension",
        "nonexistent_parent_id",
    ],
)
def test_insert_rule_invalid_data(test_db, rule):
    """Invalid rules must be rejected and must not be inserted."""
    result = insert_rule(rule, test_db)

    assert result == (False, None, "invalid_rule")

    with sqlite3.connect(test_db) as conn:
        custom_rules = conn.execute(
            "SELECT COUNT(*) FROM rules WHERE is_default = 0"
        ).fetchone()[0]

    assert custom_rules == 0


# ============================================================
# 2. UPDATE RULE TESTS
# ============================================================

# -------------------------
# 2.1 Successful update
# -------------------------

def test_update_rule_success(test_db):
    """An existing custom rule should be updated successfully."""
    rule = create_rule(".jgp_before_update")
    assert insert_rule(rule, db_path=test_db) == (True, None, "success")

    rule.value = [".jgp_after_update"]
    rule.category = "Updated"
    rule.priority = 4

    result = update_rule(rule, db_path=test_db)

    assert result == (True, None, "success")

    row = get_rule_data(test_db, rule.rule_id)
    assert row is not None
    assert row[2] == '[".jgp_after_update"]'
    assert row[3] == "Updated"
    assert row[4] == 4


def test_update_rule_with_valid_multi_level_hierarchy(test_db):
    """A rule may be moved to another valid parent in a multi-level hierarchy."""
    root = create_rule(".jgp_update_root")
    assert insert_rule(root, test_db) == (True, None, "success")

    middle = create_rule(".jgp_update_middle", parent_id=root.rule_id)
    assert insert_rule(middle, test_db) == (True, None, "success")

    leaf = create_rule(".jgp_update_leaf", parent_id=middle.rule_id)
    assert insert_rule(leaf, test_db) == (True, None, "success")

    leaf.parent_id = root.rule_id
    result = update_rule(leaf, test_db)

    assert result == (True, None, "success")
    assert get_rule_data(test_db, leaf.rule_id)[5] == root.rule_id


def test_update_rule_rejects_indirect_cycle_without_modifying_data(test_db):
    """An update that makes a rule its own ancestor must be rejected."""
    root = create_rule(".jgp_update_cycle_root")
    assert insert_rule(root, test_db) == (True, None, "success")

    middle = create_rule(".jgp_update_cycle_middle", parent_id=root.rule_id)
    assert insert_rule(middle, test_db) == (True, None, "success")

    leaf = create_rule(".jgp_update_cycle_leaf", parent_id=middle.rule_id)
    assert insert_rule(leaf, test_db) == (True, None, "success")

    original_data = get_rule_data(test_db, root.rule_id)

    # root -> leaf would create root -> leaf -> middle -> root.
    root.parent_id = leaf.rule_id
    result = update_rule(root, test_db)

    assert result == (False, None, "invalid_rule")
    assert get_rule_data(test_db, root.rule_id) == original_data


def test_update_rule_with_children_to_valid_parent_succeeds(test_db):
    """A rule with descendants can be moved if the new parent is valid."""
    first_root = create_rule(".jgp_reparent_first_root")
    second_root = create_rule(".jgp_reparent_second_root")
    assert insert_rule(first_root, test_db) == (True, None, "success")
    assert insert_rule(second_root, test_db) == (True, None, "success")

    middle = create_rule(
        ".jgp_reparent_middle",
        parent_id=first_root.rule_id,
    )
    assert insert_rule(middle, test_db) == (True, None, "success")

    leaf = create_rule(
        ".jgp_reparent_leaf",
        parent_id=middle.rule_id,
    )
    assert insert_rule(leaf, test_db) == (True, None, "success")

    middle.parent_id = second_root.rule_id
    result = update_rule(middle, test_db)

    assert result == (True, None, "success")
    assert get_rule_data(test_db, middle.rule_id)[5] == second_root.rule_id
    assert get_rule_data(test_db, leaf.rule_id)[5] == middle.rule_id


def test_update_rule_rejects_reparenting_to_own_descendant(test_db):
    """A rule cannot be moved beneath one of its own descendants."""
    root = create_rule(".jgp_reparent_cycle_root")
    assert insert_rule(root, test_db) == (True, None, "success")

    middle = create_rule(
        ".jgp_reparent_cycle_middle",
        parent_id=root.rule_id,
    )
    assert insert_rule(middle, test_db) == (True, None, "success")

    leaf = create_rule(
        ".jgp_reparent_cycle_leaf",
        parent_id=middle.rule_id,
    )
    assert insert_rule(leaf, test_db) == (True, None, "success")

    original_middle = get_rule_data(test_db, middle.rule_id)
    original_leaf = get_rule_data(test_db, leaf.rule_id)

    middle.parent_id = leaf.rule_id
    result = update_rule(middle, test_db)

    assert result == (False, None, "invalid_rule")
    assert get_rule_data(test_db, middle.rule_id) == original_middle
    assert get_rule_data(test_db, leaf.rule_id) == original_leaf


def test_update_rule_rejects_missing_intermediate_parent(test_db):
    """An update must reject a broken reference inside the parent chain."""
    root = create_rule(".jgp_broken_root")
    assert insert_rule(root, test_db) == (True, None, "success")

    middle = create_rule(".jgp_broken_middle", parent_id=root.rule_id)
    assert insert_rule(middle, test_db) == (True, None, "success")

    candidate = create_rule(".jgp_broken_candidate")
    assert insert_rule(candidate, test_db) == (True, None, "success")

    # Simulate corrupted data: middle points to a nonexistent parent.
    with sqlite3.connect(test_db) as conn:
        conn.execute(
            "UPDATE rules SET parent_id = ? WHERE id = ?",
            (999999, middle.rule_id),
        )

    original_data = get_rule_data(test_db, candidate.rule_id)
    candidate.parent_id = middle.rule_id
    result = update_rule(candidate, test_db)

    assert result == (False, None, "invalid_rule")
    assert get_rule_data(test_db, candidate.rule_id) == original_data


# -------------------------
# 2.2 Invalid and unavailable rules
# -------------------------

def test_update_rule_nonexistent(test_db):
    """A nonexistent rule should not be updated."""
    rule = create_rule(".jgp_missing_update")
    rule.rule_id = 999999

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


# -------------------------
# 2.3 Duplicate extension
# -------------------------

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
# 2.4 Invalid update data
# -------------------------

@pytest.mark.parametrize(
    "invalid_rule",
    [
        Rule(
            rule_type="extension",
            value=[".updated"],
            category="Test",
            priority=5,
            parent_id=None,
        ),
        Rule(
            rule_type="extension",
            value=["pdf"],
            category="Test",
            priority=2,
            parent_id=None,
        ),
        Rule(
            rule_type="extension",
            value=[".updated"],
            category="Test",
            priority=2,
            parent_id=999999,
        ),
    ],
    ids=[
        "invalid_priority",
        "invalid_extension",
        "nonexistent_parent_id",
    ],
)
def test_update_rule_invalid_data(test_db, invalid_rule):
    """Invalid updates must be rejected without modifying the database."""
    original_rule = create_rule(".original")
    assert insert_rule(original_rule, test_db)[0] is True

    invalid_rule.rule_id = original_rule.rule_id
    original_data = get_rule_data(test_db, original_rule.rule_id)

    result = update_rule(invalid_rule, test_db)

    assert result == (False, None, "invalid_rule")
    assert get_rule_data(test_db, original_rule.rule_id) == original_data


# ============================================================
# 3. DELETE RULE TESTS
# ============================================================

def test_delete_rule_success(test_db):
    """An existing custom rule should be deleted successfully."""
    rule = create_rule(".jgp_delete_success")
    assert insert_rule(rule, db_path=test_db) == (True, None, "success")

    result = delete_rule(rule.rule_id, db_path=test_db)

    assert result == (True, None, "success")
    assert get_rule_data(test_db, rule.rule_id) is None


# -------------------------
# 3.1 Hierarchy integrity
# -------------------------

def test_delete_rule_with_one_child_is_rejected(test_db):
    """A parent rule must not be deleted while it has a child rule."""
    parent = create_rule(".jgp_delete_parent")
    assert insert_rule(parent, test_db) == (True, None, "success")

    child = create_rule(".jgp_delete_child", parent_id=parent.rule_id)
    assert insert_rule(child, test_db) == (True, None, "success")

    parent_data = get_rule_data(test_db, parent.rule_id)
    child_data = get_rule_data(test_db, child.rule_id)

    result = delete_rule(parent.rule_id, db_path=test_db)

    assert result == (False, None, "has_children")
    assert get_rule_data(test_db, parent.rule_id) == parent_data
    assert get_rule_data(test_db, child.rule_id) == child_data


def test_delete_rule_with_multiple_children_is_rejected(test_db):
    """A parent rule must not be deleted while multiple children reference it."""
    parent = create_rule(".jgp_delete_multi_parent")
    assert insert_rule(parent, test_db) == (True, None, "success")

    first_child = create_rule(
        ".jgp_delete_multi_child_a",
        parent_id=parent.rule_id,
    )
    second_child = create_rule(
        ".jgp_delete_multi_child_b",
        parent_id=parent.rule_id,
    )

    assert insert_rule(first_child, test_db) == (True, None, "success")
    assert insert_rule(second_child, test_db) == (True, None, "success")

    parent_data = get_rule_data(test_db, parent.rule_id)
    first_child_data = get_rule_data(test_db, first_child.rule_id)
    second_child_data = get_rule_data(test_db, second_child.rule_id)

    result = delete_rule(parent.rule_id, db_path=test_db)

    assert result == (False, None, "has_children")
    assert get_rule_data(test_db, parent.rule_id) == parent_data
    assert get_rule_data(test_db, first_child.rule_id) == first_child_data
    assert get_rule_data(test_db, second_child.rule_id) == second_child_data


def test_delete_leaf_rule_with_parent_succeeds(test_db):
    """A leaf rule can be deleted without affecting its parent."""
    parent = create_rule(".jgp_delete_leaf_parent")
    assert insert_rule(parent, test_db) == (True, None, "success")

    child = create_rule(
        ".jgp_delete_leaf_child",
        parent_id=parent.rule_id,
    )
    assert insert_rule(child, test_db) == (True, None, "success")

    result = delete_rule(child.rule_id, db_path=test_db)

    assert result == (True, None, "success")
    assert get_rule_data(test_db, child.rule_id) is None
    assert get_rule_data(test_db, parent.rule_id) is not None


def test_delete_parent_after_deleting_all_children_succeeds(test_db):
    """A parent can be deleted after all its children have been removed."""
    parent = create_rule(".jgp_delete_after_children_parent")
    assert insert_rule(parent, test_db) == (True, None, "success")

    first_child = create_rule(
        ".jgp_delete_after_children_a",
        parent_id=parent.rule_id,
    )
    second_child = create_rule(
        ".jgp_delete_after_children_b",
        parent_id=parent.rule_id,
    )

    assert insert_rule(first_child, test_db) == (True, None, "success")
    assert insert_rule(second_child, test_db) == (True, None, "success")

    assert delete_rule(first_child.rule_id, db_path=test_db) == (
        True, None, "success"
    )
    assert delete_rule(second_child.rule_id, db_path=test_db) == (
        True, None, "success"
    )

    result = delete_rule(parent.rule_id, db_path=test_db)

    assert result == (True, None, "success")
    assert get_rule_data(test_db, parent.rule_id) is None


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
