from src.models.hall import Hall
from src.utils.helpers import get_valid_choice, get_non_empty_input
def hall_panel(hall_manager):
    while True:
        print("1. Add hall")
        print("2. View halls")
        print("3. Activate/deactivate hall")
        print("4. Back")
        print("5. Edit hall")

        choice = get_valid_choice(
            "Choose an option: ",
            ["1", "2", "3" ,"4","5"]
        )
        if choice == "1":
            try:
                hall_id = int(input("Hall ID: "))
                if hall_id <= 0:
                    raise ValueError("Hall ID must be positive.")
                name = get_non_empty_input("Hall name: ")
                capacity = int(input("Hall capacity: "))
                equipment = [item.strip() for item in input("Equipment (comma-separated): ").split(",") if item.strip()]

                hall = Hall(name, capacity, equipment, True)
                hall_manager.add_hall(hall_id, hall)
                print("Hall added successfully.")

            except ValueError as error:
                print("Error adding hall:", error)

        elif choice == "2":
            halls = hall_manager.view_halls()

            if not halls:
                print("No halls have been registered.")
            else:
                for hall_id, hall in halls.items():
                    print(hall_id, hall.name, hall.capacity, hall.equipment, hall.status)
        elif choice == "3":
            try:
                hall_id = int(input("Hall ID: "))

                print("1. Activate")
                print("2. Deactivate")

                action = get_valid_choice("Choose an option: ", ["1", "2"])

                if action == "1":
                    hall_manager.activate_hall(hall_id)
                else:
                    hall_manager.deactivate_hall(hall_id)

                print("Hall status updated.")

            except ValueError as error:
                print("Error:", error)

        elif choice == "4":
            break
        elif choice == "5":
            try:
                hall_id = int(input("Hall ID: "))
                hall = hall_manager.view_halls().get(hall_id)

                if hall is None:
                    print("Hall not found.")
                    continue

                name = get_non_empty_input("New hall name: ")
                capacity = int(input("New capacity: "))

                equipment = [
                    item.strip()
                    for item in input("New equipment (comma-separated): ").split(",")
                    if item.strip()
                ]

                updated_hall = Hall(
                    name, capacity, equipment, hall.status
                )

                hall_manager.edit_hall(hall_id, updated_hall)
                print("Hall updated successfully.")

            except (ValueError, OSError) as error:
                print("Error editing hall:", error)