""" This module provides functionality to manage the SQLite database for storing rules.
It includes functions to initialize the database, insert and retrieve existing information."""

import sqlite3
import json
from contextlib import contextmanager
from src.core.models import Rule  # Import the Rule class from the models module
from src.validator import RuleConflictValidator


@contextmanager
def get_connection(db_path="data/database.db"):
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()  # Commit the transaction if no exceptions occurred
    except Exception:
        conn.rollback()  # Rollback the transaction in case of an exception
        raise  # Re-raise the exception to be handled by the caller
    finally:
        conn.close()


def initialize_rules_database(db_path="data/database.db"):
    """Initialize the SQLite database and create the 'rules' table if it doesn't exist."""

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
                rule.id = result  # Update the rule's id with the last inserted row id


def insert_rule(rule, db_path="data/database.db"):
    """Insert a new rule into the database."""

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

                    rule.id = cursor.lastrowid  # Update the rule's id with the last inserted row id
                    return (True, None, "success")

            else:
                return (False, None, "rule_limit_reached")

    except sqlite3.Error:
        return (None, None, "database_error")


def get_rules():
    """Retrieve all rules from the database and return them as a list of Rule objects."""

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
    """Update an existing custom rule in the database."""

    if rule.is_default != 0:
        return (False, None, "invalid_rule")

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT is_default FROM rules WHERE id = ?',
                            (rule.id,)
                            )
            result = cursor.fetchone()

            if result is None:
                return (False, None, "invalid_rule")
            if result[0] == 1:
                return (False, None, "invalid_rule")


            validator = RuleConflictValidator(rule, conn, rule.id)
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
                rule.id
            )
            )
            if cursor.rowcount == 1:
                return (True, None, "success")
            else:
                return (None, None, "update_failed")

    except sqlite3.Error:
        return (None, None, "database_error")


def delete_rule(rule_id, db_path="data/database.db"):
    """Delete an existing custom rule in the database."""

    try:
        with get_connection(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT is_default FROM rules WHERE id = ?',
                            (rule_id,)
                            )
            result = cursor.fetchone()

            if result is None:
                return (False, None, "invalid_rule")
            if result[0] == 1:
                return (False, None, "invalid_rule")


            cursor.execute('DELETE FROM rules WHERE id = ? AND is_default = 0',
                            (rule_id,)
                            )

            if cursor.rowcount == 1:
                return (True, None, "success")
            else:
                return (None, None, "delete_failed")

    except sqlite3.Error:
        return (None, None, "database_error")
