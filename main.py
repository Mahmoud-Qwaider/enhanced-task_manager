# main.py
# ============================================================================
# CLI layer for the Enhanced Task Manager.
# Uses inquirer for menus, art/termcolor for banners, and PrettyTable for
# tabular output. Every menu choice routes to a function in PSEUDOCODE - sql.py (Database Layer).py.
# ============================================================================

import sql
from termcolor import colored
from art import *
from prettytable import PrettyTable
import inquirer


def notify_user(message):
    # Prints a green ASCII-art banner for success messages (existing helper).
    ascii_banner = text2art(message)
    print(colored(ascii_banner, 'green'))


def get_int(prompt):
    # Small helper to safely read an integer from the user. Returns None if the
    # input is empty or not a valid number, so callers can abort gracefully
    # instead of crashing on invalid input.
    raw = input(prompt).strip()
    if not raw:
        print(colored("Input cannot be empty.", 'red'))
        return None
    try:
        return int(raw)
    except ValueError:
        print(colored("Please enter a valid number.", 'red'))
        return None


def main():
    sql.create_db()
    ascii_banner = text2art("Task Manager")
    print(colored(ascii_banner, 'green'))
    print('Welcome to the Enhanced Task Manager!')
    print('This is a task manager application to manage your daily tasks \n')

    # Full menu: original choices + all newly added features, grouped logically.
    choices = [
        # --- Create ---
        'Create User',
        'Create User Details',
        'Create Task',
        'Create Tag',
        'Assign Tag to Task',
        # --- Read ---
        'Fetch All Users',
        'Fetch All Tasks',
        'Fetch All Tags',
        'View User Details',
        'List Tags for a Task',
        'List Tasks for a Tag',
        # --- Update ---
        'Update User Information',
        'Update User Details',
        'Update Task Details',
        'Update Tag Name',
        'Mark Task as Complete',
        # --- Delete ---
        'Delete User',
        'Delete User Details',
        'Delete Task',
        'Delete Tag',
        'Remove Tag from Task',
        # --- Exit ---
        'Exit'
    ]

    while True:
        action = inquirer.prompt([
            inquirer.List('action',
                          message="What do you want to do?",
                          choices=choices,
                          )
        ])['action']

        # ------------------------- Exit -------------------------
        if action == 'Exit':
            print(text2art('Bye!'))
            break

        # ------------------------- Create -------------------------
        elif action == "Create User":
            name = input("Enter Name: ")
            email = input("Enter Email: ")
            sql.create_user(name, email)
            notify_user("User Created!")

        elif action == "Create User Details":
            user_id = get_int("Enter User ID: ")
            if user_id is None:
                continue
            phone = input("Enter Phone: ")
            preferences = input("Enter Preferences: ")
            address = input("Enter Address: ")
            if sql.create_user_details(user_id, phone, preferences, address):
                notify_user("Details Added!")

        elif action == "Create Task":
            user_id = get_int("Enter User ID: ")
            if user_id is None:
                continue
            description = input("Enter Description: ")
            due_date = input("Enter Due Date (YYYY-MM-DD): ")
            status = input("Enter Status: ")
            if sql.create_task(user_id, description, due_date, status):
                notify_user("Task Created!")

        elif action == "Create Tag":
            tag_name = input("Enter Tag Name: ")
            sql.create_tag(tag_name)
            notify_user("Tag Created!")

        elif action == "Assign Tag to Task":
            # Show existing tasks and tags first, so the user doesn't have to
            # guess the IDs (fixes the "blind system" problem).
            print(colored("\nAvailable Tasks:", 'cyan'))
            tasks = sql.read_tasks()
            t_table = PrettyTable(['Task ID', 'User ID', 'Description', 'Due Date', 'Status'])
            for task in tasks:
                t_table.add_row(task)
            print(t_table)

            print(colored("\nAvailable Tags:", 'cyan'))
            tags = sql.read_tags()
            g_table = PrettyTable(['Tag ID', 'Name'])
            for tag in tags:
                g_table.add_row(tag)
            print(g_table)

            task_id = get_int("Enter Task ID: ")
            if task_id is None:
                continue
            tag_id = get_int("Enter Tag ID: ")
            if tag_id is None:
                continue
            if sql.create_task_tag_relation(task_id, tag_id):
                notify_user("Tag Assigned!")

        # ------------------------- Read -------------------------
        elif action == 'Fetch All Users':
            users = sql.read_users()
            table = PrettyTable(['ID', 'Name', 'Email'])
            for user in users:
                table.add_row(user)
            print(table)

        elif action == "Fetch All Tasks":
            tasks = sql.read_tasks()
            table = PrettyTable(
                ['Task ID', 'User ID', 'Description', 'Due Date', 'Status'])
            for task in tasks:
                table.add_row(task)
            print(table)

        elif action == "Fetch All Tags":
            # NEW. Lists every tag with its ID so the user knows which numbers
            # to use when assigning tags to tasks.
            tags = sql.read_tags()
            table = PrettyTable(['Tag ID', 'Name'])
            for tag in tags:
                table.add_row(tag)
            print(table)

        elif action == "View User Details":
            # Shows a single user joined with their extended info in one table.
            user_id = get_int("Enter User ID: ")
            if user_id is None:
                continue
            row = sql.view_user_details(user_id)
            if row is None:
                print(colored("No user found with that ID.", 'red'))
            else:
                table = PrettyTable(
                    ['User ID', 'Name', 'Email', 'Phone', 'Preferences', 'Address'])
                # Replace any NULLs (user without details) with a dash for clarity.
                table.add_row([cell if cell is not None else '-' for cell in row])
                print(table)

        elif action == "List Tags for a Task":
            task_id = get_int("Enter Task ID: ")
            if task_id is None:
                continue
            tags = sql.list_tags_for_task(task_id)
            if not tags:
                print(colored("No tags linked to this task.", 'yellow'))
            else:
                table = PrettyTable(['Tag ID', 'Name'])
                for tag in tags:
                    table.add_row(tag)
                print(table)

        elif action == "List Tasks for a Tag":
            tag_id = get_int("Enter Tag ID: ")
            if tag_id is None:
                continue
            tasks = sql.list_tasks_for_tag(tag_id)
            if not tasks:
                print(colored("No tasks linked to this tag.", 'yellow'))
            else:
                table = PrettyTable(
                    ['Task ID', 'User ID', 'Description', 'Due Date', 'Status'])
                for task in tasks:
                    table.add_row(task)
                print(table)

        # ------------------------- Update -------------------------
        elif action == "Update User Information":
            user_id = get_int("Enter User ID to update: ")
            if user_id is None:
                continue
            name = input("Enter new Name: ")
            email = input("Enter new Email: ")
            if sql.update_user_info(user_id, name, email):
                notify_user("User Updated!")
            else:
                print(colored("No user found with that ID.", 'red'))

        elif action == "Update User Details":
            details_id = get_int("Enter User Details ID to update: ")
            if details_id is None:
                continue
            phone = input("Enter new Phone: ")
            preferences = input("Enter new Preferences: ")
            address = input("Enter new Address: ")
            if sql.update_user_details(details_id, phone, preferences, address):
                notify_user("Details Updated!")
            else:
                print(colored("No details found with that ID.", 'red'))

        elif action == "Update Task Details":
            task_id = get_int("Enter Task ID to update: ")
            if task_id is None:
                continue
            description = input("Enter new Description: ")
            due_date = input("Enter new Due Date (YYYY-MM-DD): ")
            status = input("Enter new Status: ")
            if sql.update_task_details(task_id, description, due_date, status):
                notify_user("Task Updated!")
            else:
                print(colored("No task found with that ID.", 'red'))

        elif action == "Update Tag Name":
            tag_id = get_int("Enter Tag ID to rename: ")
            if tag_id is None:
                continue
            new_name = input("Enter new Tag Name: ")
            if sql.update_tag_name(tag_id, new_name):
                notify_user("Tag Renamed!")
            else:
                print(colored("No tag found with that ID.", 'red'))

        elif action == "Mark Task as Complete":
            task_id = get_int("Enter Task ID to complete: ")
            if task_id is None:
                continue
            if sql.mark_task_complete(task_id):
                notify_user("Task Done!")
            else:
                print(colored("No task found with that ID.", 'red'))

        # ------------------------- Delete -------------------------
        elif action == "Delete User":
            # Note: this cascades through the user's details, tasks, and tag links.
            user_id = get_int("Enter User ID to delete: ")
            if user_id is None:
                continue
            if sql.delete_user(user_id):
                notify_user("User Deleted!")
            else:
                print(colored("No user found with that ID.", 'red'))

        elif action == "Delete User Details":
            details_id = get_int("Enter User Details ID to delete: ")
            if details_id is None:
                continue
            if sql.delete_user_details(details_id):
                notify_user("Details Deleted!")
            else:
                print(colored("No details found with that ID.", 'red'))

        elif action == "Delete Task":
            task_id = get_int("Enter Task ID to delete: ")
            if task_id is None:
                continue
            if sql.delete_task(task_id):
                notify_user("Task Deleted!")
            else:
                print(colored("No task found with that ID.", 'red'))

        elif action == "Delete Tag":
            tag_id = get_int("Enter Tag ID to delete: ")
            if tag_id is None:
                continue
            if sql.delete_tag(tag_id):
                notify_user("Tag Deleted!")
            else:
                print(colored("No tag found with that ID.", 'red'))

        elif action == "Remove Tag from Task":
            task_id = get_int("Enter Task ID: ")
            if task_id is None:
                continue
            tag_id = get_int("Enter Tag ID to remove: ")
            if tag_id is None:
                continue
            if sql.remove_tag_from_task(task_id, tag_id):
                notify_user("Tag Removed!")
            else:
                print(colored("That tag was not linked to that task.", 'red'))


if __name__ == '__main__':
    main()
