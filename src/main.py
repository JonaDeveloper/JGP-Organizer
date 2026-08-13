from pathlib import Path
import rules, organizer
from os import access, R_OK, W_OK


def main():
    print("\n\n\t-----------------------------")
    print("\tWelcome to the JGP-Organizer!") # Display a welcome message to the user.
    print("\t-----------------------------")
    # Prompt the user to enter the directory to organize.
    directory = input("\n• Enter the directory you want to organize: ")
    
    # Create a Path object from the user-provided directory.
    p = Path(directory)
    # Initialize a counter for the number of files organized.
    count = 0
    # Initialize a counter for the number of files that could not be organized due to permission issues.  
    count_errors = 0
    
    try: # Check if the provided path is a valid directory.
        if not p.is_dir():
            raise FileNotFoundError # Raise an error if the path is not a directory.
    except FileNotFoundError: # Handle specific errors related to invalid directory paths.
        print(f"\n\t• Error: No such file or directory: {directory}\n")
    except Exception as e: # Handle any other unexpected errors that may occur during the organization process.
        print(f"\n\t• An unexpected error occurred: {e}\n")
        
    else:   
        print(f"\n\t• Organizing files...") # Display the absolute path of the directory being organized.
        
        # Iterate through every item in the current directory.
        for xfile in p.iterdir():
            if xfile.is_file() and not xfile.name.startswith('.'): # Process only files and ignore directories.
                if not access(xfile, R_OK | W_OK): # Check if the file is accessible (readable, writable).
                    count_errors += 1  # Increment the count of files that could not be organized due to permission issues.
                    print(f"\n/// Permission denied for file: {xfile}, do not organize.\n") # Notify the user if the file is not accessible.
                else:
                    try: # Attempt to classify and organize the file based on the defined rules.
                        category, file = rules.classify_file(xfile) # Detect the file category based on the defined rules.
                        organizer.organize_file(category, file) # Move the file to its corresponding destination.
                        count += 1  # Increment the count of organized files.
                        
                    except Exception as e: # Handle any errors that occur during the file organization process.  
                        print(f"\n• An error occurred while organizing {xfile}: {e}\n")
        # After processing all files, provide a summary of the organization process.
        if count == 0 and count_errors == 0:
            print(f"\n\t• No files were found in the directory '{directory}' to organize.\n")
        else:
            print(f"\n\t• Organization process completed for directory: '{directory}'\n")
            if count > 0:
                print(f"\t• {count} files organized successfully.\n")
            else:
                print(f"\t• No files were organized in directory.\n")
            if count_errors > 0:
                print(f"\t• {count_errors} files could not be organized due to permission issues. Please check the permission settings for the files.\n")
    print(f"\n• Thank you for using the JGP-Organizer! Goodbye!\n\n") # Display a farewell message to the user.


if __name__ == "__main__":
    main() # Call the main function to start the program.


