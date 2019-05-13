from utils.methods import get_response, random_string, send_email, get_cloud_storage_image_link, sign_url, analyze_post
from utils.methods import translate_post, delete_cloud_storage_content, delete_cloud_storage_folder, get_hash
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from utils.methods import locate_post
from api.database.posts import Posts
from api.database.users import Users
from http import HTTPStatus
import builtins

database = builtins.database


def check_user_token(token, username):
    try:
        users = Users.query.filter(Users.username == username).all()
    except:
        return None, get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    if len(users) == 0:
        return None, get_response(status=HTTPStatus.NOT_FOUND)

    return users[0], None

    try:
        users = Users.query.filter(Users.username == username, Users.token == token).all()
    except:
        return None, get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    if len(users) == 0:
        return None, get_response(status=HTTPStatus.FORBIDDEN)
    return users[0], None


class UsersService:

    @staticmethod
    def get_all_users():
        try:
            users = Users.query.all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(users) == 0:
            return get_response(status=HTTPStatus.NO_CONTENT)

        user_list = []
        for user in users:
            try:
                avatar = sign_url(user.avatar)
            except:
                avatar = ""

            user_list.append({
                "username": user.username,
                "avatar": avatar
            })
        return get_response(
            status=HTTPStatus.OK,
            response={
                "users": user_list
            }
        )

    @staticmethod
    def login_user(user):
        user = Users(user)

        try:
            users = Users.query.filter(Users.username == user.username, Users.password == user.password).all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(users) == 0:
            return get_response(status=HTTPStatus.UNAUTHORIZED)
        return get_response(
            status=HTTPStatus.OK,
            response={
                "token": users[0].token
            }
        )

    @staticmethod
    def add_user(user):
        user = Users(user)

        try:
            database.session.add(user)
            database.session.commit()
        except IntegrityError as exception:
            return get_response(status=Users.get_database_exception(exception))
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return get_response(
            status=HTTPStatus.CREATED,
            response={
                "token": user.token
            }
        )

    @staticmethod
    def get_new_password(user):
        user = Users(user)
        PASSWORD_SIZE = 40

        try:
            users = Users.query.filter(Users.username == user.username, Users.mail == user.mail).all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(users) == 0:
            return get_response(status=HTTPStatus.BAD_REQUEST)

        password = random_string(PASSWORD_SIZE)
        try:
            send_email(
                user.mail,
                "[Google Cloud App New Password]",
                "Hello, your new password is " + password
            )

            user = users[0]
            user.password = get_hash(password)
            database.session.commit()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)


        return get_response(status=HTTPStatus.OK)

    @staticmethod
    def get_user_info(token, username):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        try:
            avatar = sign_url(user.avatar)
        except:
            avatar = ""

        return get_response(
            status=HTTPStatus.OK,
            response={
                "user": {
                    "username": user.username,
                    "mail": user.mail,
                    "avatar": avatar
                }
            }
        )

    @staticmethod
    def patch_user(token, username, user_json, user_avatar):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        if user_json is not None:
            user.update_entry(user_json)
            try:
                database.session.commit()
            except IntegrityError as exception:
                return get_response(status=Users.get_database_exception(exception))
            except:
                return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if user_avatar is not None:
            user.avatar = get_cloud_storage_image_link('user-{}/avatar'.format(user.id), user_avatar)
            try:
                database.session.commit()
            except:
                return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return get_response(status=HTTPStatus.OK)

    @staticmethod
    def delete_user(token, username):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        try:
            delete_cloud_storage_folder("user-" + str(user.id))
            database.session.delete(user)
            database.session.commit()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return get_response(status=HTTPStatus.OK)

    @staticmethod
    def get_user_posts(username):
        try:
            users = Users.query.filter(Users.username == username).all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(users) == 0:
            return get_response(status=HTTPStatus.NOT_FOUND)

        user = users[0]
        try:
            posts = database.session.query(Users, Posts).filter(Users.id == user.id).join(
                Posts,
                Users.id == Posts.user_id
            ).all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(posts) == 0:
            return get_response(status=HTTPStatus.NO_CONTENT)

        user_posts = []
        for post in posts:
            try:
                try:
                    link = sign_url(post[1].link)
                except:
                    link = ""

                user_posts.append({
                    "id": post[1].id,
                    "title": post[1].title,
                    "description": post[1].description,
                    "link": link
                })
            except:
                pass

        return get_response(
            status=HTTPStatus.OK,
            response={
                "posts": user_posts
            })

    @staticmethod
    def add_user_post(token, username, post, image):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        post["user_id"] = user.id
        post = Posts(post)
        try:
            database.session.add(post)
            database.session.commit()

            post.link = get_cloud_storage_image_link('user-{}/image-{}'.format(user.id, post.id), image)
            database.session.commit()
        except IntegrityError as exception:
            return get_response(status=Posts.get_database_exception(exception))
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        return get_response(status=HTTPStatus.CREATED)

    @staticmethod
    def get_user_post(token, username, post_id):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        try:
            posts = Posts.query.filter(Posts.user_id == user.id, Posts.id == post_id).all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(posts) == 0:
            return get_response(status=HTTPStatus.NOT_FOUND)

        post = posts[0]
        try:
            link = sign_url(post.link)
        except:
            link = ""

        return get_response(
            status=HTTPStatus.OK,
            response={
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "link": link
            }
        )

    @staticmethod
    def patch_user_post(token, username, post_id, post_json, post_image):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        try:
            posts = Posts.query.filter(Posts.user_id == user.id, Posts.id == post_id).all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(posts) == 0:
            return get_response(status=HTTPStatus.NOT_FOUND)
        post = posts[0]

        if post_json is not None:
            post.update_entry(post_json)
            try:
                database.session.commit()
            except IntegrityError as exception:
                return get_response(status=Posts.get_database_exception(exception))
            except:
                return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if post_image is not None:
            post.link = get_cloud_storage_image_link('user-{}/image-{}'.format(user.id, post.id), post_image)
            try:
                database.session.commit()
            except:
                return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return get_response(status=HTTPStatus.OK)

    @staticmethod
    def delete_user_post(token, username, post_id):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        try:
            post = Posts.query.filter(Posts.id == post_id).one()
            delete_cloud_storage_content(post.link)
        except NoResultFound:
            return get_response(status=HTTPStatus.NOT_FOUND)
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        try:
            database.session.delete(post)
            database.session.commit()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return get_response(status=HTTPStatus.OK)

    @staticmethod
    def analyze_post(token, username, post_id):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        try:
            posts = Posts.query.filter(Posts.user_id == user.id, Posts.id == post_id).all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(posts) == 0:
            return get_response(status=HTTPStatus.NOT_FOUND)

        analyzed, response = analyze_post(posts[0])
        if response is not None:
            return response

        return get_response(
            status=HTTPStatus.OK,
            response={
                "analyzed": analyzed
            }
        )

    @staticmethod
    def translate_post(token, username, post_id, language):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        try:
            posts = Posts.query.filter(Posts.user_id == user.id, Posts.id == post_id).all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(posts) == 0:
            return get_response(status=HTTPStatus.NOT_FOUND)

        translated, response = translate_post(posts[0], language)
        if response is not None:
            return response

        return get_response(
            status=HTTPStatus.OK,
            response={
                "translated": translated
            }
        )

    @staticmethod
    def locate_post(token, username, post_id, query_data):
        user, response = check_user_token(token, username)
        if response is not None:
            return response

        try:
            posts = Posts.query.filter(Posts.user_id == user.id, Posts.id == post_id).all()
        except:
            return get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if len(posts) == 0:
            return get_response(status=HTTPStatus.NOT_FOUND)

        located, response = locate_post(posts[0], query_data)
        if response is not None:
            return response

        return get_response(
            status=HTTPStatus.OK,
            response=located
        )
