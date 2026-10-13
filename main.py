from src.auth.authentication import login
from src.utils.helpers import get_valid_choice
from src.admin.user_manager import load_user
from src.admin.admin_panel import admin_panel
from src.admin.hall_manager import HallManager
def main():
    hall_manager = HallManager()
    while True :
        print( "1.ورود مدیر باشگاه")
        print("2.ورود مربی")
        print("3.ورود عضو باشگاه")
        print("4.خروج")
        choice = get_valid_choice(
            "Enter your choice: ",
            ["1", "2", "3", "4"]
        )
        if choice == "4":
            print("موفق باشید")
            break
        try:
            users = [user.to_dict() for user in load_user()]
        except (OSError, ValueError, UnicodeError) as error:
            print("خطا در خواندن کاربران:", error)
            continue
        if choice == "1" :
            result = login("manager",users)
            if result is not None and result["success"]:
                print("welcome manager")
                admin_panel(result["username"], hall_manager)
        elif choice == "2" :
            result = login("coach",users)
            if result is not None and result["success"]:
                print("welcome coach")
        elif choice == "3" :
            result = login("member",users)
            if result is not None and result["success"]:
                print("welcome member")

if __name__ == "__main__":
    main()