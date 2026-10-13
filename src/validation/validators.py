import re
def validate_password(password):
    if not isinstance(password,str) or not password:
        return False
    if not re.search(r"[a-zA-Z]",password):
        return False
    if not re.search(r"[0-9]",password):
        return False
    if not re.search(r"[@&]",password):
        return False
    return True
def validate_email(email):
    if not isinstance(email,str) or not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.fullmatch(pattern,email) is not None
def validate_username(username):
    if not isinstance(username,str) or not username:
        return False
    pattern = r"^[a-zA-Z0-9_]{3,}$"
    return re.fullmatch(pattern,username) is not None
def validate_name(name):
    if not isinstance(name,str) or not name:
        return False
    pattern = r"^[a-zA-Zآ-ی\s]{3,}$"
    return re.fullmatch(pattern,name) is not None
def validate_no_forbidden_chars(value):
    if not isinstance(value,str):
        return False
    return "\t" not in value and "\n" not in value

        
