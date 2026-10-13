from src.auth.authentication import login,users
from src.utils.helpers import get_valid_choice
from src.admin.user_manager import load_user
def main():
    while True :
        print( "1.ورود مدیر باشگاه")
        print("2.ورود مربی")
        print("3.ورود عضو باشگاه")
        print("4.خروج")
        choice = get_valid_choice(
            "Enter your choice: ",
            ["1", "2", "3", "4"]
        )
        if choice == "1" :
            result = login("manager",users)
            if result is not None and result["success"]:
                print("welcome manager")
        elif choice == "2" :
            result = login("coach",users)
            if result is not None and result["success"]:
                print("welcome coach")
        elif choice == "3" :
            result = login("member",users)
            if result is not None and result["success"]:
                print("welcome member")
        elif choice == "4" :
            print("موفق باشید")
            break

if __name__ == "__main__":
    main()