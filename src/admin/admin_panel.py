from src.admin.user_manager import (
    add_user,
    edit_user,
    toggle_active,
    view_user,
    load_user
)
from getpass import getpass
from src.utils.helpers import get_valid_choice, get_non_empty_input, confirm_action
from src.admin.hall_panel import hall_panel
from src.admin.class_panel import class_panel
from src.member.subscription_manager import get_revenue_by_type
from src.admin.subscription_panel import subscription_panel
def admin_panel(username, hall_manager, class_manager):
    while True:
        print("1. Add User")
        print("2. View Users")
        print("3. Edit User")
        print("4. Activate/Deactivate User")
        print("5. Back to Main Menu")
        print("6. Manage Halls")
        print("7. Manage Classes")
        print("8. Subscription Revenue Report")
        print("9. Gym Statistics Report")
        print("10. Manage Subscriptions and Payments")

        choice = get_valid_choice(
            "Enter your choice: ",
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        )
        if choice == "1":
            name = get_non_empty_input("Full name: ")
            new_username = get_non_empty_input("Username: ")
            email = get_non_empty_input("Email: ")
            password = getpass("Password: ")
            if any(c in password for c in "\t\n\r"):
                print("Password contains invalid characters.")
                continue
            role = get_valid_choice(
                "User role (coach/member): ",
                ["coach", "member"]
            )
            try:
                add_user(name, new_username, password, email, role)
            except (OSError, ValueError, UnicodeError) as error:
                print("Error adding user:", error)
        elif choice == "2":
            try:
                view_user()
            except (OSError, UnicodeError) as error:
                print("Error displaying users:", error)
        elif choice == "3":
            target_username = get_non_empty_input("Enter the username to edit: ")
            print("1. Change Name")
            print("2. Change Email")
            print("3. Change Password")
            edit_choice = get_valid_choice(
                "Select an edit option: ",
                ["1", "2", "3"]
            )
            try:
                if edit_choice == "1":
                    new_name = get_non_empty_input("New name: ")
                    edit_user(target_username, new_name=new_name)
                elif edit_choice == "2":
                    new_email = get_non_empty_input("New email: ")
                    edit_user(target_username, new_email=new_email)
                elif edit_choice == "3":
                    new_password = getpass("New password: ")
                    if any(c in new_password for c in "\t\n\r"):
                        print("Password contains invalid characters.")
                    else:
                        edit_user(target_username, new_password=new_password)
            except (OSError, ValueError, UnicodeError) as error:
                print("Error editing user:", error)
        elif choice == "4":
            target_username = get_non_empty_input("Enter the username: ")
            if target_username == username:
                print("You cannot deactivate your own manager account.")
            elif confirm_action("Change user status? (y/n): "):
                try:
                    toggle_active(target_username)
                except (OSError, ValueError, UnicodeError) as error:
                    print("Error changing user status:", error)
            else:
                print("Operation cancelled.")
        elif choice == "5":
            break
        elif choice == "6":
            hall_panel(hall_manager)
        elif choice == "7":
            class_panel(class_manager)
        elif choice == "8":
            try:
                revenues = get_revenue_by_type()
                if not revenues:
                    print("No subscription revenue has been recorded yet.")
                else:
                    print("\n--- Subscription Revenue Report ---")
                    for months, amount in sorted(revenues.items()):
                        print(f"Subscription ({months} months): {amount} Toman")
                    print("Total revenue:", sum(revenues.values()), "Toman")
            except (OSError, ValueError, UnicodeError) as error:
                print("Error generating revenue report:", error)
        elif choice == "9":
            try:
                users = load_user()
                active_members = sum(
                    1 for user in users
                    if user.role == "member"
                    and user.is_active is True
                )
                active_coaches = sum(
                    1 for user in users
                    if user.role == "coach"
                    and user.is_active is True
                )
                classes = class_manager.view_classes()

                active_classes = sum(
                    1 for gym_class in classes.values()
                    if gym_class.status is True
                )
                print("\n--- Gym Statistics Report ---")
                print("Active members:", active_members)
                print("Active coaches:", active_coaches)
                print("Active classes:", active_classes)
            except (OSError, ValueError, UnicodeError) as error:
                print("Error generating statistics report:", error)
        elif choice == "10":
            subscription_panel()