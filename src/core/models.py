""" Class to represent a classification rule."""


class Rule:
    """Class to represent a classification rule."""

    def __init__(self, rule_type, value, category, priority, parent_id, is_default=0, rule_id=None):
        self.rule_id = rule_id
        self.rule_type = rule_type
        self.value = value
        self.category = category
        self.priority = priority
        self.parent_id = parent_id
        self.is_default = is_default
