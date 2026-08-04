from pathlib import Path
import rules, organizer


# Prompt the user to enter the directory to organize.
directory = input("Enter the directory you want to sortorganize: ")

# Create a Path object from the user-provided directory.
p = Path(directory)

# Ensure this code only runs when the script is executed directly.
if __name__ == "__main__":

    # Display the absolute path of the directory being organized.
    print(f"Organizing files in directory: {p.resolve()}")

    # Iterate through every item in the current directory.
    for xfile in p.iterdir():
        # Process only files and ignore directories.
        if xfile.is_file():
            # Detect the file category based on the defined rules.
            category, file = rules.classify_file(xfile)
            # Move the file to its corresponding destination.
            organizer.organize_file(category, file)

    # Indicate that the organization process has finished.
    print("Files organized successfully.")