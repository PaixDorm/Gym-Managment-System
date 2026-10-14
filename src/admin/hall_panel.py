from src.models.hall import Hall
from src.utils.helpers import get_valid_choice, get_non_empty_input
def hall_panel(hall_manager):
    while True:
        print("1.افزودن سالن")
        print("2.نمایش سالن‌ها")
        print("3.فعال/غیر فعال کردن")
        print("4.بازگشت")
        print("5. ویرایش سالن")

        choice = get_valid_choice(
            "انتخاب کنید: ",
            ["1", "2", "3" ,"4","5"]
        )
        if choice == "1":
            try:
                hall_id = int(input("شناسه سالن: "))
                if hall_id <= 0:
                    raise ValueError("شناسه سالن باید مثبت باشد")
                name = get_non_empty_input("نام سالن: ")
                capacity = int(input("ظرفیت سالن: "))
                equipment = [item.strip() for item in input("تجهیزات: ").split(",") if item.strip()]

                hall = Hall(name, capacity, equipment, True)
                hall_manager.add_hall(hall_id, hall)
                print("سالن با موفقیت اضافه شد")

            except ValueError as error:
                print("خطا در افزودن سالن:", error)

        elif choice == "2":
            halls = hall_manager.view_halls()

            if not halls:
                print("هیچ سالنی ثبت نشده")
            else:
                for hall_id, hall in halls.items():
                    print(hall_id, hall.name, hall.capacity, hall.equipment, hall.status)
        elif choice == "3":
            try:
                hall_id = int(input("شناسه سالن: "))

                print("1. فعال کردن")
                print("2. غیرفعال کردن")

                action = get_valid_choice("انتخاب: ", ["1", "2"])

                if action == "1":
                    hall_manager.activate_hall(hall_id)
                else:
                    hall_manager.deactivate_hall(hall_id)

                print("وضعیت سالن تغییر کرد")

            except ValueError as error:
                print("خطا:", error)

        elif choice == "4":
            break
        elif choice == "5":
            try:
                hall_id = int(input("شناسه سالن: "))
                hall = hall_manager.view_halls().get(hall_id)

                if hall is None:
                    print("سالن پیدا نشد")
                    continue

                name = get_non_empty_input("نام جدید سالن: ")
                capacity = int(input("ظرفیت جدید: "))

                equipment = [
                    item.strip()
                    for item in input("تجهیزات جدید (با کاما جدا کنید): ").split(",")
                    if item.strip()
                ]

                updated_hall = Hall(
                    name, capacity, equipment, hall.status
                )

                hall_manager.edit_hall(hall_id, updated_hall)
                print("سالن با موفقیت ویرایش شد")

            except (ValueError, OSError) as error:
                print("خطا در ویرایش سالن:", error)