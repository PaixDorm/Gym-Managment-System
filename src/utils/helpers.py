def get_valid_choice(prompt,valid_choices):
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        else:
            print("خطایی رخ داد")
def get_non_empty_input(prompt):
    while True :
        a = input(prompt).strip()
        if a != "":
            return a
        else :
            print("خطایی رخ داد")
def confirm_action(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else :
            print("لطفا y یا n وارد کنید")
