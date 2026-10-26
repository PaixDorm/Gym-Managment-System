from src.auth.authentication import login
from src.utils.helpers import get_valid_choice
from src.admin.user_manager import load_user
from src.admin.admin_panel import admin_panel
from src.admin.hall_manager import HallManager
from src.coach.coach_panel import CoachPanel
from src.member.member_panel import MemberPanel
from src.admin.class_manager import ClassManager
def main():
    hall_manager = HallManager()
    class_manager = ClassManager(hall_manager)
    while True :
        print("1. Manager Login")
        print("2. Coach Login")
        print("3. Member Login")
        print("4. Exit")
        choice = get_valid_choice(
            "Enter your choice: ",
            ["1", "2", "3", "4"]
        )
        if choice == "4":
            print("Thank you for using the Gym Management System. Goodbye!")
            break
        try:
            users = [user.to_dict() for user in load_user()]
        except (OSError, ValueError, UnicodeError) as error:
            print("Error loading users:", error)
            continue
        if choice == "1" :
            result = login("manager",users)
            if result is not None and result["success"]:
                print("welcome manager")
                admin_panel(result["username"], hall_manager, class_manager)
        elif choice == "2" :
            result = login("coach",users)
            if result is not None and result["success"]:
                print("welcome coach")
                CoachPanel(result["username"]).runner()
        elif choice == "3" :
            result = login("member",users)
            if result is not None and result["success"]:
                print("welcome member")
                MemberPanel(result["username"]).runner()

if __name__ == "__main__":
    main()