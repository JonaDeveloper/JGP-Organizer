"""This module contains the main function to organize files in a specified directory."""

from pathlib import Path
# Import access, R_OK, and W_OK for file permission checking
from os import access, R_OK, W_OK
import shutil  # Import the shutil module for file operations
# Import the organizer module for file organization
import src.core.organizer as organizer
import src.core.rules as rules  # Import the rules module for file classification
import src.core.models as models
from src.db import database


def main():
    """
    Initializes the rules database and runs the main application loop.

    Displays the main menu and dispatches the selected action to either
    the file organization process or the rules management interface.
    Repeats the menu until the user chooses to exit the application.

    Returns:
        bool: False when the user selects the exit option.
    """

    # Initialize the database and create the 'rules' table if it doesn't exist
    database.initialize_rules_database()

    while True:

        menu = main_menu()

        if menu == 1:
            run_organizer()

        elif menu == 2:
            manage_rules()

        elif menu == 3:
            print("\tExit the Program")
            return False


def main_menu():
    """
    Displays the main menu and prompts the user to select an option.

    Provides options to organize files, manage rules, or exit the
    application. Validates the user's input to ensure that the
    selected option is an integer between 1 and 3. Repeats the
    prompt until a valid option is selected.

    Returns:
        int: The selected menu option, ranging from 1 to 3.
    """

    option = 0

    while option not in range(1, 4):

        # Display a welcome message to the user.
        print("\n\n\t-----------------------------")
        print("\tWelcome to the JGP-Organizer!")
        print("\t-----------------------------")

        print("""
            1. Organize files
            2. Manage rules
            3. Exit
            """)

        try:
            option = int(input("\n• Select one option: "))
            if option not in range(1, 4):
                print("\t\nIncorrect option. Please select 1, 2 or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            option = 0

    return option


def manage_rules():
    """
    Manages the rule administration workflow by repeatedly displaying
    the rules menu and executing the action selected by the user.

    Supports displaying existing rules, creating custom rules, editing
    rules, and returning to the main menu. The delete rule option is
    reserved for future implementation.

    Returns:
        None: Exits the rules management loop when the user selects
        the option to return to the main menu.
    """

    while True:

        call_rule_menu = rules_menu()

        if call_rule_menu == 1:
            show_rules()
        elif call_rule_menu == 2:
            create_rule()
        elif call_rule_menu == 3:
            edit_rule()
        elif call_rule_menu == 4:
            delete_rule()
        elif call_rule_menu == 5:
            return


def rules_menu():
    """
    Displays the rules management menu and prompts the user to select
    an option.

    Provides options to show existing rules, create a custom rule,
    edit a rule, delete a rule, or return to the main menu.

    Validates the user's input to ensure that the selected option
    is an integer between 1 and 5. Repeats the prompt until a valid
    option is selected.

    Returns:
        int: The selected menu option, ranging from 1 to 5.
    """

    rules_option = 0

    while rules_option not in range(1, 6):

        # Display a welcome message to the user.
        print("\n\n\t---------------------------")
        print("\t\tManage Rules")
        print("\t---------------------------")

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
                print("\t\nIncorrect option. Please select 1, 2, 3, 4 or 5.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            rules_option = 0

    return rules_option


def show_rules():
    """
    Retrieves and displays all rules stored in the database in a
    formatted table, showing up to 10 rules per page.

    Displays each rule's ID, category, value, type, priority, and
    parent ID. Pauses after every 10 rules to allow the user to
    view the next page, except when the last page is reached.

    If no rules are found, displays a message indicating that the
    database contains no rules.

    Returns:
        list: A list of Rule objects retrieved from the database.
    """

    rules_list = database.get_rules()  # Retrieve rules from the database
    print(f"\n\n{len(rules_list)} rules loaded from the database.\n")

    page_size = 10
    # Headings
    header = (
        f"{'RuleID':<10}"
        f"{'Category':<20}"
        f"{'Value':<50}"
        f"{'Type':<12}"
        f"{'Priority':<10}"
        f"{'ParentID':<10}"
    )
    print(header)
    print("-" * len(header))

    # Display the rules 10 at a time
    if rules_list:
        for index, rule in enumerate(rules_list, start=1):
            print(
                f"{rule.rule_id:<10}"
                f"{rule.category:<20}"
                f"{str(rule.value):<50}"
                f"{rule.rule_type:<12}"
                f"{rule.priority:^10}"
                f"{str(rule.parent_id):^10}"
            )
            # Pausar cada 10 reglas, excepto al terminar
            if index % page_size == 0 and index < len(rules_list):
                input("\nPress ENTER to display the next 10 rules...")
                print()
                print(header)
                print("-" * len(header))

    else:
        print("No rules were found in the database")
        input("\nPress Enter to continue... ")

    input("\nPress Enter to continue... ")
    return rules_list


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
        value_input = input(
            "\n• Enter the file extensions, preceded by a dot e.g. (.jpg) "
            "and separated by commas: "
        ).lower().split(",")
        if not value_input or not any(x.strip() for x in value_input):
            print(
                "\tInvalid input. Please enter at least one valid file extension, "
                "starting with a dot e.g. (.jpg).")
            value = []
        else:
            for extension_text in value_input:
                extension = extension_text.strip()
                if extension.startswith('.') and len(extension) >= 2:
                    value.append(extension)
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
    while priority not in range(1, 5):
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
        rule_type=rule_type,
        value=value,
        category=category,
        priority=priority,
        parent_id=parent_id,
    )

    success, extensions, reason = database.insert_rule(rule)

    if success is True:
        # Correct Insert
        print("\n\t• The rule has been created successfully.\n")
        input("\nPress Enter to continue... ")

    elif reason == "duplicate_extension":
        # Show duplicate extensions
        print(
            "\n\t• The rule was not created; Please check that the extensions introduced "
            "are not already covered by other rules.\n"
        )
        for extension in extensions:
            print(f"• Duplicate Extension: {extension}")
        input("\nPress Enter to continue... ")

    elif reason == "rule_limit_reached":
        # Report the limit
        print(
            "\n\t• The rule was not created; You have reached the limit of 5 custom rules. "
            "To create more custom rules, purchase the Pro version.\n"
        )
        input("\nPress Enter to continue... ")

    elif reason == "database_error":
        # Report the validation error
        print(
            "\n\t• The rule was not created; An error occurred while entering the rule into the "
            "database. Please check that the rule is correct and enter it again.\n"
        )
        input("\nPress Enter to continue... ")

    elif reason == "invalid_rule":
        print(
            "\n\t• The rule contains incorrect data; please review the rule you are entering to "
            "ensure that all data is correct, then try inserting it again.\n"
        )
        input("\nPress Enter to continue... ")

    else:
        print(
            "\n\t• An unknown error has occurred; please review the rule you are entering to "
            "ensure that all data is correct, then try inserting it again.\n"
        )
        input("\nPress Enter to continue... ")


def edit_rule():
    """
        Allows the user to select and edit an existing custom rule stored
        in the database.

        Retrieves and displays the available rules, prompts the user to
        select a rule by its ID, and displays the selected rule's current
        attributes before requesting the updated values.

        Only custom rules can be modified. Default rules cannot be edited
        in the free version.

        Prompts the user to enter the new file extensions, category name,
        and priority while validating the input. Preserves the original
        rule type and parent ID, then attempts to update the rule in the
        database.

        Displays an appropriate message depending on the result of the
        update operation, including success, duplicate extensions, invalid
        rule data, database errors, or unexpected errors.

        If no rules are available, displays an error message and returns
        without attempting to edit a rule.

        Returns:
            None: The function handles user interaction and database update
            results without returning a value.
    """

    selected_rule = select_rule_to_edit()

    if not selected_rule:
        return

    if selected_rule.is_default == 0:
        header = (
            f"{'RuleID':<10}"
            f"{'Category':<20}"
            f"{'Value':<50}"
            f"{'Type':<12}"
            f"{'Priority':<10}"
            f"{'ParentID':>10}"
        )
        print(header)
        print("-" * len(header))

        print(
            f"{selected_rule.rule_id:<10}"
            f"{selected_rule.category:<20}"
            f"{str(selected_rule.value):<50}"
            f"{selected_rule.rule_type:<12}"
            f"{selected_rule.priority:^10}"
            f"{str(selected_rule.parent_id):>10}"
        )

        rule_type, value, category, priority, parent_id = get_updated_rule_data(
            selected_rule)

        rule = models.Rule(
            rule_type=rule_type,
            value=value,
            category=category,
            priority=priority,
            parent_id=parent_id,
            rule_id=selected_rule.rule_id
        )
        success, extensions, reason = database.update_rule(rule)

        if success is True:
            print("\n\t• The rule has been updated successfully.")
            input("\nPress Enter to continue... ")

        elif reason == "duplicate_extension":
            # Show duplicate extensions
            print(
                "\n\t• The rule has not been updated; please check that the extensions you entered "
                "are not already covered by other rules.\n"
            )
            for extension in extensions:
                print(f"• Duplicate Extension: {extension}")
            input("\nPress Enter to continue... ")

        elif reason == "database_error":
            # Report the validation error
            print(
                "\n\t• The rule has not been updated; an error occurred while entering the rule "
                "into the database. Please check that the rule is correct and enter it again."
            )
            input("\nPress Enter to continue... ")

        elif reason == "invalid_rule":
            print(
                "\n\t• The rule contains incorrect data; please review the rule you are updated to "
                "ensure that all data is correct, try inserting it again."
            )
            input("\nPress Enter to continue... ")

        else:
            print(
                "\n\t• An unknown error has occurred; please review the rule you are updated to "
                "ensure that all data is correct, try inserting it again."
            )
            input("\nPress Enter to continue... ")

    else:
        print(
            "\nThe rule you are trying to modify is a default rule; it is not possible "
            "to modify default rules in the free version."
        )
        input("\nPress Enter to continue... ")


def select_rule_to_edit():

    rules_db = show_rules()

    if rules_db:

        selected_rule_id = 0
        while not selected_rule_id:
            try:
                selected_rule_id = int(
                    input("\nInput the RuleID of the rule you wish to update: "))
                print("")
            except ValueError:
                print("\tInvalid input. Please enter a number.")
                selected_rule_id = 0

        selected_rule = None
        for rule in rules_db:
            if rule.rule_id == selected_rule_id:
                selected_rule = rule
                break

        if selected_rule:
            return selected_rule

        else:
            print(
                f"\tERROR: The rule {selected_rule_id} was not found in the database.")
            input("\nPress Enter to continue... ")
            return None

    else:
        print("\tERROR: There are no rules that can be edited.")
        input("\nPress Enter to continue... ")
        return None


def get_updated_rule_data(selected_rule):

    rule_type = selected_rule.rule_type

    value = []
    current_value = None
    if rule_type == "extension":
        current_value = ", ".join(selected_rule.value)

    while not value:
        value_input = input(
            "\n• Enter the file extensions, preceded by a dot e.g. (.jpg) and separated "
            f"by commas; if you prefer to keep the current settings '[{current_value}]', "
            "press Enter: "
        ).lower().strip()
        if not value_input:
            value = selected_rule.value.copy()
            break
        else:
            extensions_input = value_input.split(",")
            for extension_text in extensions_input:
                extension = extension_text.strip()
                if extension.startswith('.') and len(extension) >= 2:
                    value.append(extension)
                else:
                    print(
                        "\tERROR: 'One of your extensions is not entered correctly'")
                    value = []
                    break

    category = ""
    current_category = selected_rule.category
    while not category:
        category_input = input(
            "\n• Enter the category name; to keep the current category "
            f"'[{current_category}]', press Enter: "
        ).strip()
        if not category_input:
            category = selected_rule.category
            break
        category = category_input
        if not category:
            print(
                "\tIncorrect name. Please enter the correct category name.\n")

    priority = 0
    current_priority = selected_rule.priority
    while priority not in range(1, 5):
        try:
            priority_input = input(
                "\n• Enter the priority from 1 to 4, where 1 is the highest and 4 "
                f"is the lowest; if you prefer the current priority '[{current_priority}]', "
                "press Enter: "
            ).strip()
            if not priority_input:
                priority = selected_rule.priority
                break
            priority = int(priority_input)
            if priority not in range(1, 5):
                print("Incorrect option. Please select 1, 2, 3 or 4.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            priority = 0

    parent_id = selected_rule.parent_id

    return (rule_type, value, category, priority, parent_id)


def delete_rule():

    rules_db = show_rules()

    if rules_db:
        selected_rule_id = 0
        while not selected_rule_id:
            try:
                selected_rule_id = int(
                    input("\nEnter the RuleID of the rule you wish to delete: "))
                print("")
            except ValueError:
                print("\tInvalid input. Please enter a number.")
                selected_rule_id = 0

        selected_rule = None
        for rule in rules_db:
            if rule.rule_id == selected_rule_id:
                selected_rule = rule
                break

        if not selected_rule:
            print(
                f"\tERROR: The rule {selected_rule_id} was not found in the database.")
            input("\nPress Enter to continue... ")
            return None

        if selected_rule.is_default == 0:
            header = (
                f"{'RuleID':<10}"
                f"{'Category':<20}"
                f"{'Value':<50}"
                f"{'Type':<12}"
                f"{'Priority':<10}"
                f"{'ParentID':>10}"
            )
            print(header)
            print("-" * len(header))

            print(
                f"{selected_rule.rule_id:<10}"
                f"{selected_rule.category:<20}"
                f"{str(selected_rule.value):<50}"
                f"{selected_rule.rule_type:<12}"
                f"{selected_rule.priority:^10}"
                f"{str(selected_rule.parent_id):>10}"
            )

            delete_rule_confirm = input(
                "\n• Are you sure you want to delete the selected rule? (y/n): "
            ).strip().lower() == 'y'

            if delete_rule_confirm:
                success, extensions, reason = database.delete_rule(
                    selected_rule.rule_id)

                if success is True:
                    print("\n\t• The rule has been successfully deleted.")
                    input("\nPress Enter to continue... ")

                elif reason == "invalid_rule":
                    print(
                        "\n\t• The RuleID entered is incorrect; please review it to ensure "
                        "that all the data provided is correct."
                    )
                    input("\nPress Enter to continue... ")

                elif reason == "delete_failed":
                    print(
                        "\n\t• An error occurred while deleting the rule "
                        f"'[{selected_rule.rule_id}]'; please check that all the data "
                        "is correct and try deleting it again."
                    )
                    input("\nPress Enter to continue... ")

                elif reason == "database_error":
                    print(
                        "\n\t• The rule has not been deleted; an error occurred while attempting "
                        "to delete the rule from the database. Please verify that the "
                        "rule is correct and enter it again. "
                    )
                    input("\nPress Enter to continue... ")

                else:
                    print(
                        "\n\t• An unknown error has occurred; check the rule you are deleting "
                        "to ensure that all data is correct, and try entering it again."
                    )
                    input("\nPress Enter to continue... ")

            else:
                return None
        else:
            print(
                "\nThe rule you are trying to delete is a default rule; it is not possible "
                "to delete default rules in the free version."
            )
            input("\nPress Enter to continue... ")

    else:
        print("\tERROR: There are no rules that can be deleted.")
        input("\nPress Enter to continue... ")
        return None


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
                    category, file = rules.classify_file(
                        xfile, categories_data)
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
                print(
                    f"\t• {count_errors} files could not be organized due to permission issues."
                    "Please check the permission settings for the files.\n"
                )


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
