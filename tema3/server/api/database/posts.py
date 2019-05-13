from sqlalchemy import CheckConstraint, ForeignKey
from http import HTTPStatus
import builtins

database = builtins.database


class Posts(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = database.Column(database.Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    title = database.Column(database.String, nullable=False)
    description = database.Column(database.String, nullable=False)
    link = database.Column(database.String, default="", nullable=False)

    def __init__(self, data):
        if isinstance(data, dict):
            self.user_id = data.get("user_id", None)
            self.title = data.get("title", "")
            self.description = data.get("description", "")

    __table_args__ = (
        CheckConstraint('LENGTH(title) > 0', name="images_check"),
    )

    def update_entry(self, data):
        if isinstance(data, dict):
            if data.get("title", None) is not None:
                self.title = data["title"]
            if data.get("description", None) is not None:
                self.description = data["description"]

    @staticmethod
    def get_database_exception(exception):
        try:
            constraint = exception.orig.diag.constraint_name
        except:
            return HTTPStatus.INTERNAL_SERVER_ERROR

        if constraint == "images_check":
            return HTTPStatus.BAD_REQUEST

        return HTTPStatus.INTERNAL_SERVER_ERROR
