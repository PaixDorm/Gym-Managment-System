from src.models.file_helper import read_lines

ENROLLMENTS_FILE = "enrollments.txt"

def enrollments_per_class():
    result = {}

    for information in read_lines(ENROLLMENTS_FILE):
        information = information.split(" | ")
        class_id = information[1]
        enrollment_status = information[4]

        if enrollment_status == "active":
            if class_id in result:
                result[class_id] += 1
            else:
                result[class_id] = 1

    return result

def most_popular_classes():
    classes = enrollments_per_class()

    if not classes:
        return None
    
    most_populars = []
    most_popular_count = 0

    for class_id, count in classes.items():
        if count == most_popular_count:
            most_populars.append(class_id)
        elif count > most_popular_count:
            most_populars.clear()
            most_populars.append(class_id)
            most_popular_count = count

    return most_populars

SUBSCRIPTIONS_FILE = "subscriptions.txt"

def income_by_subscription_type():

    result = {}

    for information in read_lines(SUBSCRIPTIONS_FILE):
        information = information.split(" | ")
        subscription_type = information[2] + "months"
        subscription_amount = int(information[3])

        if subscription_type in result:
            result[subscription_type] += subscription_amount
        else:
            result[subscription_type] = subscription_amount

    return result