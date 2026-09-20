"""This module contains the main function to organize files in a specified directory."""
from pathlib import Path
from os import access, R_OK, W_OK
import shutil
import organizer
import rules



def main():
    """Main function to organize files in a specified directory."""
    print("\n\n\t-----------------------------")
    print("\tWelcome to the JGP-Organizer!") # Display a welcome message to the user.
    print("\t-----------------------------")

    # Prompt the user to choose whether to perform a dry run (simulation) or not.
    dry_run = input(
    "\n• Do you want to perform a dry run (simulation) without moving files? (y/n): "
    ).strip().lower() == 'y'

    directory = get_directory()  # Prompt the user to enter the directory to organize.
    if directory is None:
        return  # Exit the program if the provided directory is invalid.

    if not dry_run:
        # Display the absolute path of the directory being organized.
        print("\n\t• Organizing files in directory...\n")
    else:
        print("\n\t• Simulating organization in directory... \n")

    # Organize the files in the specified directory.
    count_organized, count_errors = organize_directory(directory, dry_run)

    # Display a summary of the organization process.
    show_summary(count_organized, count_errors, directory, dry_run)

    # Display a farewell message to the user.
    print("\n• Thank you for using the JGP-Organizer! Goodbye!\n\n")



def get_directory():
    """Prompt the user to enter the directory to organize and return it as a Path object."""
    directory = input("\n• Enter the directory you want to organize: ")

    # Create a Path object from the user-provided directory.
    path = Path(directory)

    # Check if the provided path is a valid directory.
    if not path.is_dir():
        print(f"\n\t• Error: No such file or directory: {directory}\n")
        return None
    return path



def organize_directory(path, dry_run):
    """Organize files in the specified directory based on their extensions."""
    # Initialize a counter for the number of files organized.
    count_organized = 0
    # Initialize a counter for the number of files that could not be organized due to problems.
    count_errors = 0
    # Create an instance of the FileOrganizer class.
    file_organizer = organizer.FileOrganizer(dry_run)

    # Iterate through every item in the current directory.
    for xfile in path.iterdir():
        # Process only files and ignore directories and hidden files (those starting with a dot).
        if xfile.is_file() and not xfile.name.startswith('.'):
            # Check if the file is accessible (readable, writable).
            if not access(xfile, R_OK | W_OK):
                # Increase the count of files that could not be organized due to problems.
                count_errors += 1
                # Notify the user if the file is not accessible.
                print(f"\n/// Permission denied for file: {xfile}, do not organize.\n")
            else:
                try: # Attempt to classify and organize the file based on the defined rules.
                    # Detect the file category based on the defined rules.
                    category, file = rules.classify_file(xfile)
                    # Move the file to its corresponding destination.
                    result = file_organizer.organize_file(file, category)
                    if result:
                        count_organized += 1  # Increment the count of organized files.
                # Handle any errors that occurer during the file organization process.
                except (FileNotFoundError, PermissionError, OSError, shutil.Error) as e:
                    # Increment the count_errors and display the error message.
                    count_errors += 1
                    print(f"\n• An error occurred while organizing {xfile}: {e}\n")
    return count_organized, count_errors  # Return the counts of organized files and errors.



def show_summary(count_organized, count_errors, directory, dry_run):
    """Display a summary of the organization process."""
    if not dry_run:
        # After processing all files, provide a summary of the organization process.
        if count_organized == 0 and count_errors == 0:
            print(f"\n\t• No files were found in the directory '{directory}' to organize.\n")
        else:
            print(f"\n\t• Organization process completed for directory: '{directory}'\n")
            if count_organized > 0:
                print(f"\t• {count_organized} files organized successfully.\n")
            else:
                print("\t• No files were organized in directory.\n")
            if count_errors > 0:
                print(f"\t• {count_errors} files could not be organized due to permission issues."
                "Please check the permission settings for the files.\n")



if __name__ == "__main__":
    main() # Call the main function to start the program.
