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
users = [{"username":"amir", "password":"amir@1234","role":"coach", "active":True},
         {"username": "ali", "password": "ali@1234", "role": "member", "active": False },
         {"username": "zahra", "password": "zahra@1234", "role": "manager", "active": True }]
def login(role,users):
    while True:
        username = input("یوزرنیم خود را وارد کنید : ")
        password = input("پسوورد خود را وارد کنید : ")
        result = authenticate_user(username, password, role, users)
        if result["success"]:
            print("Login Successful")
            return result
        else :
            print("Login Failed")
            while True:
                print("عدد مورد نظر را وارد کنید")
                print("1,برای تلاش مجدد")
                print("2.بازگشت به منوی قبلی")
                choice = input()
                if choice == "1":
                    break
                elif choice == "2":
                    return None
                else :
                    print("عدد نامعنبر مجدد تلاش کنید")