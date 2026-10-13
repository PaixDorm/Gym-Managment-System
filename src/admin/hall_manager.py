from src.models.hall import Hall

class HallManager:
    def __init__(self):
        self.halls = {}

    def add_hall(self, hall_id, hall):

       if not isinstance(hall, Hall):
         raise ValueError("سالن باید یک شیء از کلاس Hall باش")
       
       if hall_id in self.halls:
          raise ValueError("شناسه تکراری است")
       else:
           self.halls[hall_id] = hall

    def view_halls(self):
      return self.halls

    def deactivate_hall(self, hall_id):
       if hall_id not in self.halls:
            raise ValueError("سالن با این شناسه پیدا نشد")
       self.halls[hall_id].status = False

    def activate_hall(self, hall_id):
        if hall_id not in self.halls:
             raise ValueError("سالن با این شناسه پیدا نشد")
        self.halls[hall_id].status = True

    def edit_hall(self, hall_id, new_hall):
        if not isinstance(new_hall, Hall):
            raise ValueError("سالن باید یک شیء از کلاس Hall باش")
             
        if hall_id not in self.halls:
                    raise ValueError("سالن با این شناسه پیدا نشد")
        
        self.halls[hall_id] = new_hall

