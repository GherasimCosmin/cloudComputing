from utils.methods import random_string
from sqlalchemy import CheckConstraint
from http import HTTPStatus
import builtins

database = builtins.database


def random_users_token():
    TOKEN_SIZE = 40
    token = random_string(TOKEN_SIZE)

    try:
        while Users.query.filter(Users.token == token).limit(1).first() is not None:
            token = random_string(TOKEN_SIZE)
    except:
        return None
    return token


class Users(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = database.Column(database.String, unique=True, nullable=False)
    password = database.Column(database.String, nullable=False)
    mail = database.Column(database.String, unique=True, nullable=False)
    avatar = database.Column(database.String, default="", nullable=False)
    token = database.Column(database.String, default=random_users_token, unique=True, nullable=False)

    def __init__(self, data):
        if isinstance(data, dict):
            self.username = data.get("username", "")
            self.password = data.get("password", "")
            self.mail = data.get("mail", "")

    __table_args__ = (
        CheckConstraint('LENGTH(username) > 0 AND LENGTH(password) > 0 AND LENGTH(mail) > 0', name="users_check"),
    )

    def update_entry(self, data):
        if isinstance(data, dict):
            if data.get("username", None) is not None:
                self.username = data["username"]
            if data.get("password", None) is not None:
                self.password = data["password"]
            if data.get("mail", None) is not None:
                self.mail = data["mail"]

    @staticmethod
    def get_database_exception(exception):
        try:
            constraint = exception.orig.diag.constraint_name
        except:
            return HTTPStatus.INTERNAL_SERVER_ERROR

        for field in ["username", "mail"]:
            if constraint == "users_" + field + "_key":
                return HTTPStatus.CONFLICT

        if constraint == "users_check":
            return HTTPStatus.BAD_REQUEST

        return HTTPStatus.INTERNAL_SERVER_ERROR
