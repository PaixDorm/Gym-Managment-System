from datetime import datetime
from src.models.gym_class import GymClass
from src.utils.helpers import (
    get_valid_choice,
    get_non_empty_input
)
def class_panel(class_manager):
    while True:
        print("\n--- Class Management ---")
        print("1. Add class")
        print("2. View classes")
        print("3. Activate/deactivate class")
        print("4. Back")
        print("5. Edit class")

        choice = get_valid_choice(
            "Choose an option: ", ["1", "2", "3", "4" , "5"]
        )
        if choice == "1":
            try:
                class_id = int(input("Class ID: "))
                if class_id <= 0:
                    raise ValueError("ID must be positive.")
                title = get_non_empty_input("Class name: ")
                sport = get_non_empty_input("Sport: ")
                coach = get_non_empty_input("Coach username: ")
                hall = int(input("Hall ID: "))
                day = get_non_empty_input("Day of the week: ")
                clock = get_non_empty_input("Time (HH:MM): ")
                class_time = datetime.strptime(
                    clock, "%H:%M"
                ).time()
                capacity = int(input("Class capacity: "))
                gym_class = GymClass(
                    title=title,
                    sport=sport,
                    coach=coach,
                    time=class_time,
                    day=day,
                    hall=hall,
                    capacity=capacity,
                    status=True
                )
                class_manager.add_class(class_id, gym_class)
                print("Class added successfully.")
            except (ValueError, OSError) as error:
                print("Error adding class:", error)
        elif choice == "2":
            classes = class_manager.view_classes()
            if not classes:
                print("No classes have been registered.")
            else:
                for class_id, gym_class in classes.items():
                    print(
                        "ID:", class_id,
                        "| Name:", gym_class.title,
                        "| Coach:", gym_class.coach,
                        "| Hall:", gym_class.hall,
                        "| Capacity:", gym_class.capacity,
                        "| Active:", gym_class.status
                    )
        elif choice == "3":
            try:
                class_id = int(input("Class ID: "))
                action = get_valid_choice(
                    "1. Activate / 2. Deactivate: ",
                    ["1", "2"]
                )
                if action == "1":
                    class_manager.activate_class(class_id)
                else:
                    class_manager.deactivate_class(class_id)
                print("Class status updated.")
            except (ValueError, OSError) as error:
                print("Error:", error)
        elif choice == "4":
            break
        elif choice == "5":
            try:
                class_id = int(input("Class ID: "))
                old_class = class_manager.view_classes().get(class_id)

                if old_class is None:
                    print("Class not found.")
                    continue

                title = get_non_empty_input("New class name: ")
                sport = get_non_empty_input("Sport: ")
                coach = get_non_empty_input("Coach username: ")
                hall = int(input("Hall ID: "))
                day = get_non_empty_input("Day of the week: ")

                clock = get_non_empty_input("Time (HH:MM): ")
                class_time = datetime.strptime(clock, "%H:%M").time()

                capacity = int(input("New capacity: "))

                updated_class = GymClass(
                    title=title,
                    sport=sport,
                    coach=coach,
                    time=class_time,
                    day=day,
                    hall=hall,
                    capacity=capacity,
                    status=old_class.status
                )

                class_manager.edit_class(class_id, updated_class)
                print("Class updated successfully.")

            except (ValueError, OSError) as error:
                print("Error editing class:", error)