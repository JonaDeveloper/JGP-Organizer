"""This module provides functionality to organize files into folders based on their extensions."""
import shutil


# Move a file to its corresponding category folder.
def organize_file(category, file):
    """Move a file to its corresponding category folder."""
    # Create the destination folder inside the file's parent directory.
    destination_folder = file.parent / category
    destination_folder.mkdir(exist_ok=True)

    # Build the full destination path for the file.
    destination_file = destination_folder / file.name

    # Check if a file with the same name already exists.
    if destination_file.exists():
        # Handle the duplicate file.
        handle_duplicate(file, destination_folder)
    else:
        # Move the file to the destination folder.
        shutil.move(str(file), str(destination_file))


def handle_duplicate(file, destination_folder):
    """Handle duplicate files by assigning a unique namebefore moving them to the Duplicates folder.
    """
    # Create the Duplicates folder if it does not exist.
    duplicates_folder = destination_folder / "Duplicates"
    duplicates_folder.mkdir(exist_ok=True)

    # Initialize the duplicate counter.
    counter = 1

# Start with "(1)" as the suffix for the first duplicate.
    candidate_name = f"{file.stem}({counter}){file.suffix}"
    duplicate_path = duplicates_folder / candidate_name

    # Keep generating a new filename until an available one is found.
    while duplicate_path.exists():
        counter += 1
        candidate_name = f"{file.stem}({counter}){file.suffix}"
        duplicate_path = duplicates_folder / candidate_name

    # Move the file using the unique filename.
    shutil.move(str(file), str(duplicate_path))
