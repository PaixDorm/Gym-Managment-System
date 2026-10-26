import os
from src.models.user import User
from src.validation.validators import (validate_name,validate_username,validate_password,validate_email)
USERS_FILE = "data/users.txt"
def load_user():
    if not os.path.exists(USERS_FILE):
       return []
    users = []
    with open(USERS_FILE,"r",encoding="utf-8") as f:
        for line in f:
            line = line.rstrip('\n')
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) != 6:
                raise ValueError("Invalid record format in users file.")
            name , username,password,email,role,is_active_str = parts
            if is_active_str == "True":
                is_active = True
            elif is_active_str == "False":
                is_active = False
            else:
                raise ValueError("Invalid user status.")
            user = User(name=name,username=username,password=password,email=email,role=role,is_active=is_active)
            users.append(user)
    return users
def save_user(users):
    os.makedirs("data",exist_ok=True)
    tmp_file = USERS_FILE + ".tmp"
    with open(tmp_file,"w",encoding="utf-8") as f:
        for user in users:
            fields = [user.name,user.username,user.password,user.email,user.role]
            if any("\t" in str(f) or "\n" in str(f) for f in fields):
                raise ValueError("Invalid character in user data.")
            line = f"{user.name}\t{user.username}\t{user.password}\t{user.email}\t{user.role}\t{str(user.is_active)}\n"
            f.write(line)
    os.replace(tmp_file,USERS_FILE)
def find_username(username):
    users = load_user()
    for user in users:
        if user.username == username:
            return user
    return None
def add_user(name,username,password,email,role,is_active=True):
    if not validate_name(name):
        print("Invalid name.")
        return False
    if not validate_username(username):
        print("Invalid username.")
        return False
    if not validate_password(password):
        print("Invalid password.")
        return False
    if not validate_email(email):
        print("Invalid email address.")
        return False
    if role not in ["coach" , "member"]:
        print("Invalid user role.")
        return False
    try:
        users = load_user()
    except ValueError as e:
        print(f"Error reading users file: {e}")
        return False
    for user in users:
        if user.username == username:
            print("Duplicate username.")
            return False
    new_user = User(name=name,username=username,password=password,email=email,role=role,is_active=is_active)
    users.append(new_user)
    try:
        save_user(users)
    except Exception as e:
        print(f"Error saving user: {e}")
        return False
    print("User added successfully.")
    return True
def edit_user(username,new_name=None,new_password=None,new_email=None,new_is_active=None):
    try:
        users = load_user()
    except ValueError as e:
        print(f"Error reading users file: {e}")
        return False
    target = None
    for user in users:
        if user.username == username:
            target = user
            break
    if target is None:
        print("Username not found.")
        return False
    if new_name is not None:
        if not validate_name(new_name):
            print("Invalid new name.")
            return False
        target.name = new_name
    if new_password is not None:
        if not validate_password(new_password):
            print("Invalid new password.")
            return False
        target.password = new_password
    if new_email is not None:
        if not validate_email(new_email):
            print("Invalid new email address.")
            return False
        target.email = new_email
    if new_is_active is not None:
        if not isinstance(new_is_active, bool):
            print("Invalid user status.")
            return False
        target.is_active = new_is_active
    try:
        save_user(users)
    except Exception as e:
        print(f"Error saving user: {e}")
        return False
    print("User updated successfully.")
    return True
def toggle_active(username):
    try:
        users = load_user()
    except ValueError as e:
        print(f"Error reading users file: {e}")
        return False
    target = None
    for user in users:
        if user.username == username:
            target = user
            break
    if target is None:
        print("Username not found.")
        return False
    target.is_active = not target.is_active
    try:
        save_user(users)
    except Exception as e:
        print(f"Error saving user status: {e}")
        target.is_active = not target.is_active
        return False
    if target.is_active:
        print("User account activated successfully.")
    else:
        print("User account deactivated successfully.")
    return True
def view_user():
    try:
        users = load_user()
    except ValueError as e:
        print(f"Error reading users file: {e}")
        return
    if not users:
        print("No users found.")
        return
    for user in users:
        if user.is_active:
            status = "Active"
        else:
            status = "Inactive"
        print(f"{user.name}|{user.username}|{user.role}|{user.email}|{status}")
    print(f"Total users: {len(users)}")
def save_user_report():
    try:
        users = load_user()
    except ValueError as e:
        print(f"Error reading users file: {e}")
        return False
    if not users:
        print("No users found.")
        return False
    coaches = []
    members = []
    for user in users:
        if user.role == "coach":
            coaches.append(user)
        else:
            members.append(user)
    os.makedirs("data",exist_ok=True)
    report_file = "data/user.txt"
    with open(report_file,"w",encoding="utf-8") as f:
        f.write("User Report:\n")
        f.write("Coaches:\n")
        for user in coaches:
            f.write(f"{user.name}/{user.username}\n")
        f.write("Members:\n")
        for user in members:
            f.write(f"{user.name}/{user.username}\n")
        f.write(f"Total users: {len(users)}\n")
        f.write(f"Total coaches: {len(coaches)}\n")
        f.write(f"Total members: {len(members)}\n")
    print("User report saved successfully.")
    return True

    





