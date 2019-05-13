import builtins

database = builtins.database


class Keys(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True, nullable=False)
    api_key = database.Column(database.String, unique=True, nullable=False)
