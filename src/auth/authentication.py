from src.logging.activity_logger import log_action
from src.admin.user_manager import load_user
@log_action
def authenticate_user(username, password, role, users):
    for user in users :
        if username == user["username"]:
            if password == user["password"]:
                if role == user["role"]:
                    if user["is_active"]:
                        return {"success": True,"username": user["username"],"role": user["role"]}
                    else :
                        return {"success": False,"username": None ,"role": None}
                else :
                    return {"success":False ,"username": None,"role": None}
            else :
                return {"success": False,"username": None,"role":None}
    return {"success": False, "username": None, "role": None}
def login(role, users):
    while True:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        result = authenticate_user(username, password, role, users)
        if result["success"]:
            print("Login Successful")
            return result
        else:
            print("Login Failed")
            while True:
                print("Please choose an option:")
                print("1. Try Again")
                print("2. Back to Previous Menu")
                choice = input("Enter your choice: ")
                if choice == "1":
                    break
                elif choice == "2":
                    return None
                else:
                    print("Invalid choice. Please try again.")
