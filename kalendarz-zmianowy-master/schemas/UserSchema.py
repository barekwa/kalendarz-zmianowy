class UserCreateRequest:
    def __init__(self, username, mail, password):
        self.username = username
        self.mail = mail
        self.password = password

    def to_dict(self):
        return {
            "username": self.username,
            "mail": self.mail,
            "password": self.password
        }


class UserLoginRequest:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password
        }
