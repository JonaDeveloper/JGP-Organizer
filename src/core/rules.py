"""This module provides functionality to classify files based on their extensions."""


# Determine the category of a file based on its extension.
def classify_file(xfile, categories_data):
    """Classify a file based on its extension and return the corresponding category."""
    # Get the file extension in lowercase to ensure case-insensitive matching.
    file_extension = xfile.suffix.lower()

    ordered_rules = sorted(categories_data, key=lambda rule: rule.priority)

    # Iterate through the category mapping to find the matching category for the file extension.
    for rules in ordered_rules:
        for category in rules.value:
        # Check if the file extension belongs to the current category.
            if file_extension == category:
                # Return the detected category and the original file.
                return rules.category, xfile
    # If the file extension does not match any category, return 'Others'.
    return "Others", xfile
