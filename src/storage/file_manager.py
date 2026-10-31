def read_file(path):
    try:
        with open(path,"r",encoding='utf-8') as file :
            content = file.read()
            return content
    except FileNotFoundError :
        print("File not found.")
        return None
    except PermissionError :
        print("Permission denied while reading the file.")
        return None
    except UnicodeError :
        print("Unable to decode the file using UTF-8.")
        return None
    except OSError :
        print("File read failed.")
        return None
def write_file(path,content):
    try:
        with open(path,"w",encoding="utf-8") as file :
            file.write(content)
            return True
    except PermissionError:
        print("Permission denied while writing the file.")
        return False
    except UnicodeError :
        print("Unable to encode the file content.")
        return False
    except OSError :
        print("File write failed.")
        return False
def append_file(path,content):
    try :
        with open(path,"a",encoding="utf-8") as file :
            file.write(content)
            return True
    except OSError :
        print("File append failed.")
        return False
    except UnicodeError :
        print("Unable to encode the appended content.")
        return False
def update_file(path,old_content,new_content):
    content = read_file(path)
    if content is None:
        return False
    if old_content in content:
        if old_content == "":
            return  False
        else :
            updated_file = content.replace(old_content,new_content)
            write_result=write_file(path,updated_file)
            if write_result:
                return True
            else :
                return False
    else :
        return False
