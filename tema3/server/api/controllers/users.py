from utils.methods import extract_request_body_json, check_json_dict, get_response, check_form_data_image
from utils.methods import extract_request_form_data_dict, check_language_format, get_valid_number
from utils.methods import get_request_token, object_to_dict
from api.services.users import UsersService
from http import HTTPStatus


class UsersController:

    @staticmethod
    def get_all_users():
        return UsersService.get_all_users()

    @staticmethod
    def login_user(client_request):
        json_fields = [("username", str), ("password", str)]
        user = extract_request_body_json(client_request)
        if user is None:
            return get_response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        if check_json_dict(user, json_fields) is False:
            return get_response(status=HTTPStatus.BAD_REQUEST)

        return UsersService.login_user(user)

    @staticmethod
    def add_user(client_request):
        json_fields = [("username", str), ("password", str), ("mail", str)]
        user = extract_request_body_json(client_request)
        if user is None:
            return get_response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        if check_json_dict(user, json_fields) is False:
            return get_response(status=HTTPStatus.BAD_REQUEST)
        return UsersService.add_user(user)

    @staticmethod
    def get_new_password(client_request):
        json_fields = [("username", str), ("mail", str)]
        user = extract_request_body_json(client_request)
        if user is None:
            return get_response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        if check_json_dict(user, json_fields) is False:
            return get_response(status=HTTPStatus.BAD_REQUEST)

        return UsersService.get_new_password(user)

    @staticmethod
    def get_user_info(client_request, username):
        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        return UsersService.get_user_info(token, username)

    @staticmethod
    def patch_user(client_request, username):
        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        json_fields = [("username", str), ("password", str), ("mail", str)]
        user_data = extract_request_form_data_dict(client_request)
        if user_data is None:
            return get_response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        user_json = object_to_dict(user_data, json_fields)
        patch_json, patch_avatar = check_json_dict(user_json, json_fields, False), None

        if client_request.files.get('avatar', None) is not None:
            patch_avatar, response = check_form_data_image(client_request, 'avatar')
            if response is not None:
                return get_response(status=response)

        if patch_json is False and patch_avatar is None:
            return get_response(status=HTTPStatus.BAD_REQUEST)
        return UsersService.patch_user(token, username, user_json if patch_json else None, patch_avatar)

    @staticmethod
    def delete_user(client_request, username):
        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        return UsersService.delete_user(token, username)

    @staticmethod
    def get_user_posts(username):
        return UsersService.get_user_posts(username)

    @staticmethod
    def add_user_post(client_request, username):
        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        json_fields = [("title", str), ("description", str)]
        data = extract_request_form_data_dict(client_request)
        if data is None:
            return get_response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        post = {
            "title": data.get("title", None),
            "description": data.get("description", None)
        }
        if check_json_dict(post, json_fields) is False:
            return get_response(status=HTTPStatus.BAD_REQUEST)

        image, response = check_form_data_image(client_request, 'image')
        if response is not None:
            return get_response(status=response)
        return UsersService.add_user_post(token, username, post, image)

    @staticmethod
    def get_user_post(client_request, username, post_id):
        post_id = get_valid_number(post_id)
        if post_id is None:
            return get_response(status=HTTPStatus.NOT_FOUND)

        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        return UsersService.get_user_post(token, username, post_id)

    @staticmethod
    def patch_user_post(client_request, username, post_id):
        post_id = get_valid_number(post_id)
        if post_id is None:
            return get_response(status=HTTPStatus.NOT_FOUND)

        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        json_fields = [("title", str), ("description", str)]
        user_post_data = extract_request_form_data_dict(client_request)
        if user_post_data is None:
            return get_response(status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE)

        user_post_json = object_to_dict(user_post_data, json_fields)
        patch_json, patch_image = check_json_dict(user_post_json, json_fields, False), None

        if client_request.files.get('image', None) is not None:
            patch_image, response = check_form_data_image(client_request, 'image')
            if response is not None:
                return get_response(status=response)

        if patch_json is False and patch_image is None:
            return get_response(status=HTTPStatus.BAD_REQUEST)
        return UsersService.patch_user_post(token, username, post_id, user_post_json, patch_image)

    @staticmethod
    def delete_user_post(client_request, username, post_id):
        post_id = get_valid_number(post_id)
        if post_id is None:
            return get_response(status=HTTPStatus.NOT_FOUND)

        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        return UsersService.delete_user_post(token, username, post_id)

    @staticmethod
    def analyze_post(client_request, username, post_id):
        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        post_id = get_valid_number(post_id)
        if post_id is None:
            return get_response(status=HTTPStatus.NOT_FOUND)

        return UsersService.analyze_post(token, username, post_id)

    @staticmethod
    def translate_post(client_request, username, post_id):
        language = client_request.args.get("lang", None)
        post_id = get_valid_number(post_id)

        if post_id is None:
            return get_response(status=HTTPStatus.NOT_FOUND)

        if check_language_format(language) is False:
            return get_response(status=HTTPStatus.BAD_REQUEST)

        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        return UsersService.translate_post(token, username, post_id, language)

    @staticmethod
    def locate_post(client_request, username, post_id):
        token = get_request_token(client_request)
        if token is None:
            return get_response(status=HTTPStatus.UNAUTHORIZED)

        post_id = get_valid_number(post_id)
        if post_id is None:
            return get_response(status=HTTPStatus.NOT_FOUND)

        zoom = get_valid_number(client_request.args.get("zoom", None))
        width = get_valid_number(client_request.args.get("width", None))
        height = get_valid_number(client_request.args.get("height", None))

        if zoom is None or width is None or height is None:
            return get_response(status=HTTPStatus.BAD_REQUEST)

        return UsersService.locate_post(token, username, post_id, {
            "zoom": zoom,
            "width": width,
            "height": height
        })
