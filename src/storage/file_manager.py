def read_file(path):
    try:
        with open(path,"r",encoding='utf-8') as file :
            content = file.read()
            return content
    except FileNotFoundError :
        print("فایل پیدا نشد")
        return None
    except PermissionError :
        print("اجازه خواندن فایل وجود ندارد")
        return None
    except UnicodeError :
        print("امکان خواندن با اینکودینگ مورد نظر وجد ندارد")
        return None
    except OSError :
        print("اجرا با خطا مواجه شد")
        return None
def write_file(path,content):
    try:
        with open(path,"w",encoding="utf-8") as file :
            file.write(content)
            return True
    except PermissionError:
        print("نوشتن ممکن نمیباشد")
        return False
    except UnicodeError :
        print("هنگام نوشتن خظایی رخ داد")
        return False
    except OSError :
        print("جرا با خطا مواجه شد")
        return False
def append_file(path,content):
    try :
        with open(path,"a",encoding="utf-8") as file :
            file.write(content)
            return True
    except OSError :
        print("خطایی رخ داد")
        return False
    except UnicodeError :
        print("هنگام اینکود کردن خطایی رخ داد")
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
