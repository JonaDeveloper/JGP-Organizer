from config import classify, unclassified

# Determine the category of a file based on its extension.
def classify_file(file):
    # Get the file extension in lowercase to ensure case-insensitive matching.
    extension = file.suffix.lower()

    # Retrieve the corresponding category or use the default category if the extension is not recognized.
    category = classify.get(extension, unclassified)

    # Return the detected category and the original file.
    return category, file