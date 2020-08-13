class User():
    def __init__(self, username, password, idNumber, memberSince):
        self.username = username
        self.password = password
        self.idNumber = idNumber
        self.memberSince = memberSince

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.idNumber)
