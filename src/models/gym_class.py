from datetime import time as Time

class GymClass:
    def __init__(self, title, sport, coach, time, day, hall, capacity, status):

        if not isinstance(title, str) or not title.strip():
            raise ValueError("Class name cannot be empty.")
        self.title = title
        
        if not isinstance(sport, str) or not sport.strip():
            raise ValueError("Sport cannot be empty.")
        self.sport = sport

        if not isinstance(coach, str) or not coach.strip():
           raise ValueError("Invalid coach username.")
        self.coach = coach

        if not isinstance(time, Time):
            raise ValueError("Class time must be a time object.")
        self.time = time

        if not isinstance(day, str) or not day.strip():
            raise ValueError("Class day cannot be empty.")
        self.day = day

        if type(hall) is not int:
            raise ValueError("Please enter a valid integer.")
        if hall <= 0:
            raise ValueError("Value must be greater than zero.")
        self.hall = hall

        if type(capacity) is not int:
            raise ValueError("Please enter a valid integer.")
        if capacity <= 0:
            raise ValueError("Value must be greater than zero.")
        self.capacity = capacity

        if not type(status) is bool:
            raise ValueError("Status must be a boolean.")
        self.status = status