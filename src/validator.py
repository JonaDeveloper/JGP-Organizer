"""Validator for rule attributes."""

import re
import sqlite3
import json


class RuleValidator:
    """
    Validates rule attributes to ensure they meet the required
    constraints before the rules are processed or stored.
    """

    allowed_types = ["extension", "name", "regex", "size"]

    def __init__(self, rule, rule_ids):
        self.rule = rule
        self.rule_ids = rule_ids

    def validate_type(self):
        """
        Checks whether the rule type is supported.
        Returns:
            bool: True if the rule type is allowed, False otherwise.
        """
        return self.rule.type in self.allowed_types

    def validate_value(self):
        """
        Validates the rule value according to its type.

        Supported types:
            - extension: A non-empty list of strings starting with '.'.
            - name: A non-empty string.
            - regex: A non-empty string containing a valid regular expression.
            - size: A dictionary containing a valid operator, a positive numeric amount,
                    and a supported unit (KB, MB, GB, or TB).

        Returns:
            bool: True if the value meets the requirements for its type, False otherwise.
        """
        if self.rule.type == "extension":
            return (
                isinstance(self.rule.value, list)
                and len(self.rule.value) > 0
                and all(isinstance(ext, str) and ext.startswith('.')
                        for ext in self.rule.value
                        )
            )

        # Validate the value for the "name" type.
        elif self.rule.type == "name":
            return isinstance(self.rule.value, str) and len(self.rule.value) > 0

        # Validate the value for the "regex" type.
        elif self.rule.type == "regex":
            if not isinstance(self.rule.value, str) or len(self.rule.value) == 0:
                return False
            try:
                re.compile(self.rule.value)
                return True
            except re.error:
                return False

        # Validate the value for the "size" type.
        elif self.rule.type == "size":
            return (
                isinstance(self.rule.value, dict)
                and "operator" in self.rule.value
                and self.rule.value["operator"] in [">", "<", ">=", "<=", "==", "!="]
                and "amount" in self.rule.value
                and isinstance(self.rule.value["amount"], (int, float))
                and self.rule.value["amount"] > 0
                and "unit" in self.rule.value
                and self.rule.value["unit"] in ["KB", "MB", "GB", "TB"]
            )

        else:
            return False

    def validate_priority(self):
        """
        Checks whether the rule priority is an integer between 1 and 4, inclusive.
        Returns:
            bool: True if the priority is valid, False otherwise.
        """
        return isinstance(self.rule.priority, int) and self.rule.priority in range(1, 5)

    def validate_parent_id(self):
        """
        Checks whether the parent_id is None or matches an existing rule ID.
        Returns:
            bool: True if the parent_id is valid, False otherwise.
        """
        return self.rule.parent_id is None or self.rule.parent_id in self.rule_ids

    def validate_rule(self):
        """
        Validates all supported attributes of the rule.
        Checks the rule type, value, priority, and parent ID independently.
        Returns:
            dict: A dictionary mapping each attribute name to a boolean
            indicating whether its validation passed.
        """
        return {
            "type": self.validate_type(),
            "value": self.validate_value(),
            "priority": self.validate_priority(),
            "parent_id": self.validate_parent_id()
        }


class RuleConflictValidator:
    """ 
    Validates new rules against existing rules stored in the database
    to detect conflicts, specifically duplicate file extensions.
    """

    def __init__(self, new_rule, connection, rule_id=None):
        self.new_rule = new_rule
        self.connection = connection
        self.rule_id = rule_id

    def validate_conflicts(self):
        """
        Checks whether the new rule conflicts with extensions already
        registered in the database.

        Queries rules of type 'extension' and compares their values with
        those of the new rule, returning any matching extensions.

        Returns:
            tuple:
                - bool | None: True if conflicts are found, False if no 
                                conflicts exist, or None if a database error occurs.
                - tuple | None: A tuple of conflicting extensions,
                                or None if no conflicts are found.
                - str: Result code ('duplicate_extension', 'success', or 'database_error').
        """

        consult = self.new_rule.value

        try:
            result = self.connection.execute(
                """
                SELECT DISTINCT r.id, r.category, j.value AS extension
                FROM rules AS r,
                    json_each(r.value) AS j
                WHERE (? IS NULL OR r.id != ?)
                AND r.type = 'extension'
                AND j.value IN (
                    SELECT value
                    FROM json_each(?)
                )
            """, (
                    self.rule_id,
                    self.rule_id,
                    json.dumps(consult),
                )
            )

            rows = result.fetchall()

            if rows:
                conflicts = {row[2] for row in rows}
                return (True, tuple(conflicts), "duplicate_extension")
            else:
                return (False, None, "success")

        except sqlite3.Error:
            return (None, None, "database_error")
