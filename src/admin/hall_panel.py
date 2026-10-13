from src.models.hall import Hall
from src.utils.helpers import get_valid_choice, get_non_empty_input
def hall_panel(hall_manager):
    while True:
        print("1.افزودن سالن")
        print("2.نمایش سالن‌ها")
        print("3.بازگشت")

        choice = get_valid_choice(
            "انتخاب کنید: ",
            ["1", "2", "3"]
        )
    hall_manager.add_hall(hall_id, hall)
    hall_manager.view_halls()