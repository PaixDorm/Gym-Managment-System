import re
def validate_password(password):
    if not password:
        return False
    if not re.search(r"[a-zA-Z]",password):
        return False
    if not re.search(r"[0-9]",password):
        return False
    if not re.search(r"[@&]",password):
        return False
    return True
def validate_email(email):
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.fullmatch(pattern,email) is not None
def validate_username(username):
    if not username:
        return False
    pattern = r"^[a-zA-Z0-9_]{3,}$"
    return re.fullmatch(pattern,username) is not None
def validate_name(name):
    if not name:
        return False
    pattern = r"^[\w\s]{3,}$"
    return re.fullmatch(pattern,name) is not None

        
