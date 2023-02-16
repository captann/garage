from flask_login import UserMixin

class UserLogin(UserMixin):
    def fromDb(self, user_id, db):
        self.__user = db.get_user(user_id) #list
        return self

    def create(self, user: list):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user[0]['id'])