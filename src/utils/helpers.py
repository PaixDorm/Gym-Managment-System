def get_valid_choice(prompt,valid_choices):
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        else:
            print("Invalid choice. Please try again.")
def get_non_empty_input(prompt):
    while True :
        a = input(prompt).strip()
        if a != "":
            return a
        else :
            print("Input cannot be empty. Please try again.")
def confirm_action(prompt):
    while True:
        answer = input(prompt).strip().lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False
        else :
            print("Please enter 'y' or 'n'.")
