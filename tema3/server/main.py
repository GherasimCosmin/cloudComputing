from google.oauth2.service_account import Credentials
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
from flask_cors import CORS
import builtins
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SENDGRID_API_KEY'] = os.environ['SENDGRID_API_KEY']
app.config['SENDGRID_SENDER'] = os.environ['SENDGRID_SENDER']
app.config['GOOGLE_MAPS_API_KEY'] = os.environ['GOOGLE_MAPS_API_KEY']

app.config['CLOUD_STORAGE_BUCKET'] = os.environ['CLOUD_STORAGE_BUCKET']
app.config['GOOGLE_APPLICATION_CREDENTIALS'] = Credentials.from_service_account_file(
    os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
)

database = SQLAlchemy(app)
CORS(app)

builtins.app = app
builtins.database = database

from api.controllers.users import UsersController
from utils.methods import require_api_key


@app.route("/", methods=["GET"])
def test():
    return "hello22234"


@app.route("/users", methods=["GET"])
@require_api_key
def endpoint_users():
    return UsersController.get_all_users()


@app.route("/users/login", methods=["POST"])
@require_api_key
def endpoint_login():
    return UsersController.login_user(request)


@app.route("/users/register", methods=["POST"])
@require_api_key
def endpoint_user_register():
    return UsersController.add_user(request)


@app.route("/users/recover", methods=["POST"])
@require_api_key
def endpoint_get_new_password():
    return UsersController.get_new_password(request)


@app.route("/users/<username>", methods=["GET", "PATCH", "DELETE"])
@require_api_key
def endpoint_user_account(username):
    if request.method == "GET":
        return UsersController.get_user_info(request, username)
    elif request.method == "PATCH":
        return UsersController.patch_user(request, username)
    elif request.method == "DELETE":
        return UsersController.delete_user(request, username)


@app.route("/users/<username>/posts", methods=["GET", "POST"])
@require_api_key
def endpoint_user_posts(username):
    if request.method == "GET":
        return UsersController.get_user_posts(username)
    elif request.method == "POST":
        return UsersController.add_user_post(request, username)


@app.route("/users/<username>/posts/<id>", methods=["GET", "PATCH", "DELETE"])
@require_api_key
def endpoint_user_post(username, id):
    if request.method == "GET":
        return UsersController.get_user_post(request, username, id)
    elif request.method == "PATCH":
        return UsersController.patch_user_post(request, username, id)
    elif request.method == "DELETE":
        return UsersController.delete_user_post(request, username, id)


@app.route("/users/<username>/posts/<id>/analyze")
@require_api_key
def endpoint_analyze_post(username, id):
    return UsersController.analyze_post(request, username, id)


@app.route("/users/<username>/posts/<id>/translate")
@require_api_key
def endpoint_translate_post(username, id):
    return UsersController.translate_post(request, username, id)


@app.route("/users/<username>/posts/<id>/locate")
@require_api_key
def endpoint_locate_post(username, id):
    return UsersController.locate_post(request, username, id)


if __name__ == '__main__':
    API_PORT, API_HOST = 8085, '127.0.0.1'
    database.create_all()
    app.run(host=API_HOST, port=API_PORT, debug=True)
