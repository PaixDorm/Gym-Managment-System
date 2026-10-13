from src.utils.helpers import get_valid_choice

def class_panel(class_manager):
    while True:
        print("1. افزودن کلاس")
        print("2. نمایش کلاس‌ها")
        print("3. فعال/غیرفعال کردن کلاس")
        print("4. بازگشت")

        choice = get_valid_choice(
            "گزینه موردنظر: ",
            ["1", "2", "3", "4"]
        )
        if choice == "2":
            classes = class_manager.view_classes()

            if not classes:
                print("هیچ کلاسی ثبت نشده")
            else:
                for class_id, gym_class in classes.items():
                    print(
                        class_id,
                        gym_class.title,
                        gym_class.sport,
                        gym_class.coach,
                        gym_class.day,
                        gym_class.time,
                        gym_class.capacity,
                        gym_class.status
                    )
        elif choice == "4":
            break
        elif choice in ("1", "3"):
            print("این بخش بعد از اتصال نسخه جدید عاطفه فعال می‌شود")