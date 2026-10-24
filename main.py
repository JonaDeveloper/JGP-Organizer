"""This module contains the main function to organize files in a specified directory."""

from pathlib import Path # Import the Path class from the pathlib module for handling file paths
from os import access, R_OK, W_OK # Import access, R_OK, and W_OK for file permission checking
import shutil # Import the shutil module for file operations
import src.core.organizer as organizer # Import the organizer module for file organization
import src.core.rules as rules # Import the rules module for file classification
import src.core.models as models
from src.db import database
# from src.validator import RuleValidator # Import the RuleValidator class for rule validation


def main():
    """Main function to organize files in a specified directory."""

    # Initialize the database and create the 'rules' table if it doesn't exist
    database.initialize_rules_database()

    while True:

        # Display a welcome message to the user.
        print("\n\n\t-----------------------------")
        print("\tWelcome to the JGP-Organizer!")
        print("\t-----------------------------")

        menu = main_menu()

        if menu == 1:
            run_organizer()

        elif menu == 2:
            manage_rules()

        elif menu == 3:
            print("\tExit the Program")
            return False


def main_menu():
    """Display the main menu and return the selected option."""

    option = 0

    while option not in range(1, 4):
        print("""
            1. Organize files
            2. Manage rules
            3. Exit
            """)

        try:
            option = int(input("\n• Select one option: "))
            if option not in range(1, 4):
                print("Incorrect option. Please select 1, 2 or 3.")

        except ValueError:
            print("Invalid input. Please enter a number.")
            option = 0

    return option


def manage_rules():
    """ok"""
    while True:

        # Display a welcome message to the user.
        print("\n\n\t---------------------------")
        print("\t\tManage Rules")
        print("\t---------------------------")

        call_rule_menu = rules_menu()

        if call_rule_menu == 1:
            show_rules()
        elif call_rule_menu == 2:
            create_rule()
        elif call_rule_menu == 3:
            pass
        elif call_rule_menu == 4:
            pass
        elif call_rule_menu == 5:
            return


def rules_menu():
    """ok"""
    rules_option = 0

    while rules_option not in range(1, 6):
        print("""
            1. Show rules.
            2. Create custom rule.
            3. Edit rule.
            4. Delete rule.
            5. Return to main menu.
            """)
        try:
            rules_option = int(input("\n• Select one option: "))
            if rules_option not in range(1, 6):
                print("Incorrect option. Please select 1, 2, 3, 4 or 5.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            rules_option = 0

    return rules_option


def show_rules():
    """Test"""

    rules_list = database.get_rules()  # Retrieve rules from the database

    if rules_list:
        print(f"\n\n{len(rules_list)} rules loaded from the database.\n")
        for rule in rules_list:
            print(f" Rule ID: {rule.rule_id}  \tCategory: {rule.category} \tValue: {rule.value} "
                f"\tType: {rule.rule_type} \tPriority: {rule.priority} "
                f"\tParent ID: {rule.parent_id}     \tIs Default: {rule.is_default}")

        input("\nPress Enter to return to the menu... ")

    else:
        print("No rules were found in the database")
        input("\nPress Enter to return to the menu... ")


def create_rule():
    """
    Prompts the user to enter the details of a new extension rule
    and attempts to save it to the database.

    Collects and validates the file extensions, category name, and
    priority through interactive user input. Sets the parent_id to None
    and creates a Rule instance with the collected data.

    Depending on the database insertion result, displays a success
    message or an appropriate error message for duplicate extensions,
    the custom rule limit, or a database error.
    """

    rule_type = "extension"

    value = []
    while not value:
        enter = input("\n• Enter the file extensions, preceded by a dot e.g. (.jpg) "
                        "and separated by commas: ").lower().split(",")
        if not enter or not any(x.strip() for x in enter):
            print("\tInvalid input. Please enter at least one valid file extension, "
                    "starting with a dot e.g. (.jpg).")
            value = []
        else:
            for spaces in enter:
                word = spaces.strip()
                if word.startswith('.') and len(word) >= 2:
                    value.append(word)
                else:
                    print("\tERROR: 'One of your extensions is not entered correctly'")
                    value = []
                    break

    category = ""
    while not category:
        category = input("\n• Enter the category name: ").strip()
        if not category:
            print("\tIncorrect name. Please enter the correct category name.\n")

    priority = 0
    while priority not in range(1,5):
        try:
            priority = int(input(
                "\n• Enter the priority from 1 to 4 where 1 is the highest and 4 is the lowest: "))
            if priority not in range(1, 5):
                print("Incorrect option. Please select 1, 2, 3 or 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            priority = 0

    parent_id = None

    rule = models.Rule(
                rule_type = rule_type,
                value = value,
                category = category,
                priority = priority,
                parent_id = parent_id,
                )

    success, extensions, reason = database.insert_rule(rule)

    if success is True:
        # Correct Insert
        print("\n\t• The rule has been created successfully.\n")
        input("\nPress Enter to return to the menu... ")

    elif reason == "duplicate_extension":
        # Show duplicate extensions
        print("\n\t• The rule was not created; Please check that the extensions introduced "
                    "are not already covered by other rules.\n")
        for extension in extensions:
            print(f"• Duplicate Extension: {extension}")
        input("\nPress Enter to return to the menu... ")

    elif reason == "rule_limit_reached":
        # Report the limit
        print("\n\t• The rule was not created; You have reached the limit of 5 custom rules. "
                    "To create more custom rules, purchase the Pro version.\n")
        input("\nPress Enter to return to the menu... ")

    elif reason == "database_error":
        # Report the validation error
        print("\n\t• The rule was not created; An error occurred while entering the rule into the "
                    "database. Please check that the rule is correct and enter it again.\n")
        input("\nPress Enter to return to the menu... ")

    elif reason == "invalid_rule":
        print("\n\t• The rule contains incorrect data; please review the rule you are entering to "
                    "ensure that all data is correct, then try inserting it again.\n")
        input("\nPress Enter to return to the menu... ")

    else:
        print("\n\t• An unknown error has occurred; please review the rule you are entering to "
                    "ensure that all data is correct, then try inserting it again.\n")
        input("\nPress Enter to return to the menu... ")


def run_organizer():
    """
    Runs the file organization process by prompting the user to choose
    between a dry run simulation and actual file organization.

    Requests the target directory, exits if the directory is invalid,
    and displays a message indicating the selected operation mode.
    Calls organize_directory() to process the files and show_summary()
    to display the results, including the number of organized files
    and errors encountered.

    Displays a farewell message when the process is complete.
    """

    # Prompt the user to choose whether to perform a dry run (simulation) or not.
    dry_run = input(
        "\n• Do you want to perform a dry run (simulation) without moving files? (y/n): "
    ).strip().lower() == 'y'

    # Prompt the user to enter the directory to organize.
    directory = get_directory()
    if directory is None:
        return # Exit the program if the provided directory is invalid.

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
    else:
        return path


def organize_directory(path, dry_run):
    """Organize files in the specified directory based on their rules."""

    # Initialize a counter for the number of files organized.
    count_organized = 0
    # Initialize a counter for the number of files that could not be organized due to problems.
    count_errors = 0
    # Create an instance of the FileOrganizer class.
    file_organizer = organizer.FileOrganizer(dry_run)

    categories_data = database.get_rules()  # Retrieve rules from the database

    # Iterate through every item in the current directory.
    for xfile in path.iterdir():
        # Process only files and ignore directories and hidden files (those starting with a dot).
        if xfile.is_file() and not xfile.name.startswith('.'):
            # Check if the file is accessible (readable, writable).
            if not access(xfile, R_OK | W_OK):
                # Increase the count of files that could not be organized due to problems.
                count_errors += 1
                # Notify the user if the file is not accessible.
                print(
                    f"\n/// Permission denied for file: {xfile}, do not organize.\n")
            else:
                try:  # Attempt to classify and organize the file based on the defined rules.
                    # Detect the file category based on the defined rules.
                    category, file = rules.classify_file(xfile, categories_data)
                    # Move the file to its corresponding destination.
                    result = file_organizer.organize_file(file, category)
                    if result:
                        # Increment the count of organized files.
                        count_organized += 1
                # Handle any errors that occurer during the file organization process.
                except (FileNotFoundError, PermissionError, OSError, shutil.Error) as e:
                    # Increment the count_errors and display the error message.
                    count_errors += 1
                    print(
                        f"\n• An error occurred while organizing {xfile}: {e}\n")
    # Return the counts of organized files and errors.
    return count_organized, count_errors


def show_summary(count_organized, count_errors, directory, dry_run):
    """Display a summary of the organization process."""

    if not dry_run:
        # After processing all files, provide a summary of the organization process.
        if count_organized == 0 and count_errors == 0:
            print(
                f"\n\t• No files were found in the directory '{directory}' to organize.\n")
        else:
            print(
                f"\n\t• Organization process completed for directory: '{directory}'\n")
            if count_organized > 0:
                print(f"\t• {count_organized} files organized successfully.\n")
            else:
                print("\t• No files were organized in directory.\n")
            if count_errors > 0:
                print(f"\t• {count_errors} files could not be organized due to permission issues."
                    "Please check the permission settings for the files.\n")




# rules_list = database.get_rules()
# rule_ids = [rule.id for rule in rules_list]
# rule_validator = RuleValidator(rule=rules_list[0], rule_ids=rule_ids)
# rule_validated = all(rule_validator.validate_rule().values())
# validation_results = rule_validator.validate_rule()


# if rule_validated:
    # print("\n\t• Rule is valid.\n")
# else:
    # for attribute, is_valid in validation_results.items():
        # if is_valid:
            # print(f"\n\t• Rule attribute '{attribute}' is valid.")
        # else:
            # print(f"\n\t• Rule attribute '{attribute}' is invalid.")







if __name__ == "__main__":
    main()  # Call the main function to start the program.
