"""
Provides database operations for managing file organization rules.

This module handles SQLite database initialization, connection management,
and CRUD operations for file organization rules. It supports the creation
of default rules, insertion of custom rules, retrieval of stored rules,
updates, and deletion of custom rules.

Rule values are serialized to JSON when stored and deserialized when
retrieved. Custom rule insertion and updates include conflict checks to
prevent duplicate file extensions, while default rules are protected
from modification and deletion.

The module uses a context manager to manage database connections and
transactions, ensuring that changes are committed on success and rolled
back when an exception occurs.
"""

import sqlite3
import json
from contextlib import contextmanager
from src.core.models import Rule
from src.validator import RuleConflictValidator


@contextmanager
def get_connection(db_path="data/database.db"):
    """
    Provides a database connection using a context manager.

    Opens a connection to the SQLite database and yields it for use
    within a with statement. Commits the transaction if the operations
    complete successfully, rolls back the transaction if an exception
    occurs, and closes the connection in all cases.

    Args:
        db_path (str, optional): The path to the SQLite database file.
            Defaults to "data/database.db".

    Yields:
        sqlite3.Connection: An active database connection.

    Raises:
        Exception: Re-raises any exception raised during the database
                operations after rolling back the transaction.
    """

    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def initialize_rules_database(db_path="data/database.db"):
    """
    Initializes the rules database by creating the rules table if it
    does not already exist and inserting the default rules when the
    table is empty.

    Creates the table with columns for the rule ID, type, value,
    category, priority, parent ID, and default rule status.

    Defines the default rules for common file categories, including
    images, videos, documents, audio, archives, and executables.
    Serializes rule values to JSON when necessary before inserting
    them into the database.

    Assigns each inserted default rule its generated database ID.

    Args:
        db_path (str, optional): The path to the SQLite database file.
            Defaults to "data/database.db".

    Returns:
        None: Initializes the database without returning a value.
    """

    # Use the context manager to handle the database connection
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            value TEXT NOT NULL,
            category TEXT NOT NULL,
            priority INTEGER NOT NULL,
            parent_id INTEGER,
            is_default INTEGER NOT NULL DEFAULT 0
        )''')

        if not any(row for row in cursor.execute('SELECT * FROM rules')):
            # Insert default rules if the table is empty
            default_rules = [
                Rule(
                    rule_type="extension",
                    value=[".jpg", ".png", ".gif", ".bmp", ".webp"],
                    category="Images",
                    priority=1,
                    parent_id=None,
                    is_default=1,
                ),
                Rule(
                    rule_type="extension",
                    value=[".mp4", ".avi", ".mov", ".wmv", ".mkv"],
                    category="Videos",
                    priority=1,
                    parent_id=None,
                    is_default=1
                ),
                Rule(
                    rule_type="extension",
                    value=[".pdf", ".docx", ".xls", ".xlsx", ".pptx"],
                    category="Documents",
                    priority=1,
                    parent_id=None,
                    is_default=1
                ),
                Rule(
                    rule_type="extension",
                    value=[".mp3", ".wav", ".flac", ".aac", ".ogg"],
                    category="Audio",
                    priority=1,
                    parent_id=None,
                    is_default=1
                ),
                Rule(
                    rule_type="extension",
                    value=[".zip", ".rar", ".7z", ".tar", ".gz"],
                    category="Archives",
                    priority=1,
                    parent_id=None,
                    is_default=1
                ),
                Rule(
                    rule_type="extension",
                    value=[".exe", ".msi", ".bat", ".app", ".dmg"],
                    category="Executables",
                    priority=1,
                    parent_id=None,
                    is_default=1
                )
            ]
            for rule in default_rules:
                # Convert the value to a JSON string if it's not already a string
                rule_value = rule.value if isinstance(
                    rule.value, str) else json.dumps(rule.value)

                cursor.execute('''
                INSERT INTO rules (type, value, category, priority, parent_id, is_default)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    rule.rule_type,
                    rule_value,
                    rule.category,
                    rule.priority,
                    rule.parent_id,
                    rule.is_default
                )
                )
                result = cursor.lastrowid
                rule.rule_id = result  # Update the rule's id with the last inserted row id


def insert_rule(rule, db_path="data/database.db"):
    """
    Inserts a new custom rule into the database after validating its
    eligibility and checking for conflicts with existing extensions.

    Verifies that the rule is not a default rule and checks whether
    the maximum limit of five custom rules has been reached. If the
    limit has not been reached, validates the rule for extension
    conflicts before inserting it into the database.

    Serializes the rule value to JSON if it is not already a string.
    After a successful insertion, assigns the generated database ID
    to the rule instance.

    Args:
        rule: The Rule instance containing the attributes to insert.
        db_path (str, optional): The path to the SQLite database file.
            Defaults to "data/database.db".

    Returns:
        tuple:
            - bool | None: True if the rule is inserted successfully,
                False if the rule is invalid, contains conflicting
                extensions, or the custom rule limit has been reached.
                None if a database error occurs.
            - tuple | None: A tuple containing conflicting extensions
                if a conflict is detected, or None otherwise.
            - str: Result code indicating the outcome, such as
                'success', 'invalid_rule', 'duplicate_extension',
                'rule_limit_reached', or 'database_error'.
    """

    if rule.is_default != 0:
        return (False, None, "invalid_rule")

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM rules WHERE is_default = 0')
            result = cursor.fetchone()

            if result[0] < 5:

                validator = RuleConflictValidator(rule, conn)
                has_conflict, extensions, reason = validator.validate_conflicts()

                if has_conflict is True:
                    return (False, extensions, reason)

                if has_conflict is None:
                    return (None, None, reason)

                else:
                    # Convert the value to a JSON string if it's not already a string
                    rule_value = rule.value if isinstance(
                        rule.value, str) else json.dumps(rule.value)

                    cursor.execute('''
                    INSERT INTO rules (type, value, category, priority, parent_id, is_default)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        rule.rule_type,
                        rule_value,
                        rule.category,
                        rule.priority,
                        rule.parent_id,
                        rule.is_default
                    )
                    )
                    # Update the rule's id with the last inserted row id
                    rule.rule_id = cursor.lastrowid
                    return (True, None, "success")

            else:
                return (False, None, "rule_limit_reached")

    except sqlite3.Error:
        return (None, None, "database_error")


def get_rules():
    """
    Retrieves all rules stored in the database and converts them into
    Rule instances.

    Executes a query to fetch all records from the rules table and
    reconstructs each rule, deserializing JSON values into Python lists
    or dictionaries when applicable.

    Returns:
        list: A list of Rule objects containing the stored attributes,
        including rule ID, type, value, category, priority, parent ID,
        and default rule status.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM rules')
        rows = cursor.fetchall()

        rules_list = []
        for row in rows:
            rule = Rule(
                rule_id=row[0],
                rule_type=row[1],
                # Convert JSON string back to list/dict if applicable
                value=json.loads(row[2])
                if row[2].startswith('[') or row[2].startswith('{') else row[2],
                category=row[3],
                priority=row[4],
                parent_id=row[5],
                is_default=row[6]
            )
            rules_list.append(rule)
    return rules_list


def update_rule(rule, db_path="data/database.db"):
    """
    Updates an existing custom rule in the database.

    Verifies that the rule is not a default rule and that its
    identifier corresponds to an existing custom rule. Checks for
    conflicts with existing extensions before updating the rule.

    Serializes the rule value to JSON when it is not a string, then
    updates the rule's type, value, category, priority, and parent ID.

    Args:
        rule: The Rule instance containing the updated attributes
            and the identifier of the rule to update.
        db_path (str, optional): The path to the SQLite database file.
            Defaults to "data/database.db".

    Returns:
        tuple:
            - bool | None: True if the rule is updated successfully,
                False if the rule is invalid or has conflicting extensions,
                or None if a database error or update failure occurs.
            - tuple | None: A tuple of conflicting extensions if a
                conflict is detected, or None otherwise.
            - str: Result code indicating the outcome, such as
                'success', 'invalid_rule', 'duplicate_extension',
                'update_failed', or 'database_error'.
    """

    if rule.is_default != 0:
        return (False, None, "invalid_rule")

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                'SELECT is_default FROM rules WHERE id = ?',
                (rule.rule_id,)
            )
            result = cursor.fetchone()

            if result is None:
                return (False, None, "invalid_rule")
            if result[0] == 1:
                return (False, None, "invalid_rule")

            validator = RuleConflictValidator(rule, conn, rule.rule_id)
            has_conflict, extensions, reason = validator.validate_conflicts()

            if has_conflict is True:
                return (False, extensions, reason)
            if has_conflict is None:
                return (None, None, reason)

            rule_value = rule.value if isinstance(
                rule.value, str) else json.dumps(rule.value)

            cursor.execute('''
            UPDATE rules
            SET type = ?, value = ?, category = ?, priority = ?, parent_id = ?
            WHERE id = ? AND is_default = 0
            ''', (
                rule.rule_type,
                rule_value,
                rule.category,
                rule.priority,
                rule.parent_id,
                rule.rule_id
            )
            )
            if cursor.rowcount == 1:
                return (True, None, "success")
            else:
                return (None, None, "update_failed")

    except sqlite3.Error:
        return (None, None, "database_error")


def delete_rule(rule_id, db_path="data/database.db"):
    """
    Deletes a custom rule from the database using its identifier.

    Checks whether the specified rule exists and prevents the deletion
    of default rules. Deletes the rule only if it exists and is not
    marked as a default rule.

    Args:
        rule_id (int): The identifier of the rule to delete.
        db_path (str, optional): The path to the SQLite database file.
            Defaults to "data/database.db".

    Returns:
        tuple:
            - bool | None: True if the rule is deleted successfully,
                False if the rule is invalid, or None if the deletion
                fails or a database error occurs.
            - None: Placeholder for additional result data.
            - str: Result code: 'success', 'invalid_rule',
                'delete_failed', or 'database_error'.
    """

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                'SELECT is_default FROM rules WHERE id = ?',
                (rule_id,)
            )
            result = cursor.fetchone()

            if result is None:
                return (False, None, "invalid_rule")
            if result[0] == 1:
                return (False, None, "invalid_rule")

            cursor.execute(
                'DELETE FROM rules WHERE id = ? AND is_default = 0',
                (rule_id,)
            )

            if cursor.rowcount == 1:
                return (True, None, "success")
            else:
                return (None, None, "delete_failed")

    except sqlite3.Error:
        return (None, None, "database_error")
