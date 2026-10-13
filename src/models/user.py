class User:
    def __init__(self,name,username,password,email,role,is_active=True):
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.role = role if role else "member"
        self.is_active = is_active
    def to_dict(self):
        return {"name" : self.name , 
                "username" : self.username,
                "password" : self.password,
                "email" : self.email,
                "role" : self.role,
                "is_active" : self.is_active}
    @classmethod
    def from_dict(cls,data):
        return cls(name=data.get("name",""),username=data.get("username",""),password=data.get("password",""),
                   email=data.get("email",""),role=data.get("role","member"),is_active=data.get("is_active",True))
    
    
    
    
