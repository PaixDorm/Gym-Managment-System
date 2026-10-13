from functools import wraps
import inspect
import datetime
from src.storage.file_manager import append_file
def save_log(action,role,username,success):
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_tex="|".join([time,action,role,username,str(success)])
    log_tex += "\n"
    result = append_file("data/activity_logs.txt",log_tex)
    return result
def log_action(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        bound = inspect.signature(func).bind(*args, **kwargs)
        username = bound.arguments.get("username", "system")
        role = bound.arguments.get("role", "system")
        try:
            result = func(*args,**kwargs)
        except Exception :
            save_log(func.__name__, role, username, False)
            raise
        if isinstance(result, dict):
            success = result.get("success", False)
        else:
            success = bool(result)
        save_log(func.__name__, role, username, success)

        return result
    return wrapper
