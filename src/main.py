from pathlib import Path
import rules, organizer

# Create a Path object pointing to the current working directory.
p = Path('.')

# Ensure this code only runs when the script is executed directly.
if __name__ == "__main__":

    # Display the absolute path of the directory being organized.
    print(f"Organizing files in directory: {p.resolve()}")

    # Iterate through every item in the current directory.
    for xfile in p.iterdir():
        # Process only files and ignore directories.
        if xfile.is_file():
            # Detect the file category based on the defined rules.
            category, file = rules.detection(xfile)
            # Move the file to its corresponding destination.
            organizer.organize_file(category, file)

    # Indicate that the organization process has finished.
    print("Files organized successfully.")