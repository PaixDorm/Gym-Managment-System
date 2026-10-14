from datetime import datetime
from src.models.gym_class import GymClass
from src.utils.helpers import (
    get_valid_choice,
    get_non_empty_input
)
def class_panel(class_manager):
    while True:
        print("\n--- مدیریت کلاس‌ها ---")
        print("1. افزودن کلاس")
        print("2. نمایش کلاس‌ها")
        print("3. فعال/غیرفعال کردن کلاس")
        print("4. بازگشت")

        choice = get_valid_choice(
            "انتخاب: ", ["1", "2", "3", "4"]
        )
        if choice == "1":
            try:
                class_id = int(input("شناسه کلاس: "))
                if class_id <= 0:
                    raise ValueError("شناسه باید مثبت باشد")
                title = get_non_empty_input("نام کلاس: ")
                sport = get_non_empty_input("رشته ورزشی: ")
                coach = get_non_empty_input("نام کاربری مربی: ")
                hall = int(input("شناسه سالن: "))
                day = get_non_empty_input("روز برگزاری: ")
                clock = get_non_empty_input("ساعت (HH:MM): ")
                class_time = datetime.strptime(
                    clock, "%H:%M"
                ).time()
                capacity = int(input("ظرفیت کلاس: "))
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
                print("کلاس با موفقیت اضافه شد")
            except (ValueError, OSError) as error:
                print("خطا در افزودن کلاس:", error)
        elif choice == "2":
            classes = class_manager.view_classes()
            if not classes:
                print("هیچ کلاسی ثبت نشده")
            else:
                for class_id, gym_class in classes.items():
                    print(
                        "شناسه:", class_id,
                        "| نام:", gym_class.title,
                        "| مربی:", gym_class.coach,
                        "| سالن:", gym_class.hall,
                        "| ظرفیت:", gym_class.capacity,
                        "| فعال:", gym_class.status
                    )
        elif choice == "3":
            try:
                class_id = int(input("شناسه کلاس: "))
                action = get_valid_choice(
                    "1. فعال / 2. غیرفعال: ",
                    ["1", "2"]
                )
                if action == "1":
                    class_manager.activate_class(class_id)
                else:
                    class_manager.deactivate_class(class_id)
                print("وضعیت کلاس تغییر کرد")
            except (ValueError, OSError) as error:
                print("خطا:", error)
        elif choice == "4":
            break