"""This module provides functionality to classify files based on their extensions."""
import json

# Load the category mapping from a JSON file.
with open("categories.json", "r", encoding="utf-8") as file:
    categories_data = json.load(file) # Parse the JSON data into a Python dictionary


# Determine the category of a file based on its extension.
def classify_file(xfile):
    """Classify a file based on its extension and return the corresponding category."""
    # Get the file extension in lowercase to ensure case-insensitive matching.
    file_extension = xfile.suffix.lower()

    # Iterate through the category mapping to find the matching category for the file extension.
    for category, extensions in categories_data.items():
        # Check if the file extension belongs to the current category.
        if file_extension in extensions:
            # Return the detected category and the original file.
            return category, xfile
        else:
            # If the file extension does not match any category, return 'Others'.
            return "Others", xfile
