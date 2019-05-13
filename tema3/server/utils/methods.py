from google.cloud.vision import ImageAnnotatorClient, types as gcv_types
from google.cloud.storage._signing import generate_signed_url
from google.cloud.language import types as gcl_types
from google.api_core.exceptions import BadRequest
from werkzeug.datastructures import FileStorage
from string import ascii_letters, digits
from google.cloud.language import enums
from api.database.api_keys import Keys
from google.cloud import translate
from google.cloud import language
from sendgrid.helpers import mail
from google.cloud import storage
from pycountry import languages
from datetime import timedelta
from sendgrid import sendgrid
from json import loads, dumps
from http import HTTPStatus
from random import choice
from flask import request
from six import wraps
from re import match
import builtins
import hashlib

app = builtins.app
database = builtins.database

ALLOWED_EXTENSIONS = ["image/jpeg", "image/png", "image/bmp"]
MB_SIZE = 10
MAX_FILE_SIZE = MB_SIZE * 1024 * 1024


def check_json_dict(json_data, requirements, all_fields_necessary=True):
    if json_data is None:
        return False

    all_fields, at_least_one_field = True, False
    for field_name, field_type in requirements:
        if json_data.get(field_name, None) is None or not isinstance(json_data[field_name], field_type):
            all_fields = False
        else:
            at_least_one_field = True

    return all_fields if all_fields_necessary else at_least_one_field


def extract_request_body_json(client_request):
    content_type = client_request.content_type
    if content_type != "application/json":
        return None

    try:
        json_data = loads(client_request.data.decode())
    except:
        json_data = dict()
    return json_data


def extract_request_form_data_dict(client_request):
    content_type = client_request.content_type
    if "multipart/form-data" not in content_type:
        return None

    try:
        return client_request.form
    except:
        return None


def get_response(status, response=None, mimetype="application/json"):
    return app.response_class(
        response="" if response is None else dumps(response),
        status=status,
        mimetype=mimetype
    )


def random_string(size):
    return "".join([choice(ascii_letters + digits) for _ in range(size)])


def send_email(to, subject, text):
    sg = sendgrid.SendGridAPIClient(apikey=app.config["SENDGRID_API_KEY"])
    to_email = mail.Email(to)
    from_email = mail.Email(app.config["SENDGRID_SENDER"])

    content = mail.Content('text/plain', text)
    message = mail.Mail(from_email, subject, to_email, content)

    sg.client.mail.send.post(request_body=message.get())


def check_form_data_image(client_request, field_name):
    if client_request.content_length > MAX_FILE_SIZE:
        return None, HTTPStatus.REQUEST_ENTITY_TOO_LARGE

    image = client_request.files.get(field_name, None)
    if image is None or not isinstance(image, FileStorage) or image.mimetype not in ALLOWED_EXTENSIONS:
        return None, HTTPStatus.BAD_REQUEST

    return image, None


def sign_url(filename, expiration=10):
    if len(filename) > 0 and expiration > 0:
        return generate_signed_url(
            credentials=app.config['GOOGLE_APPLICATION_CREDENTIALS'],
            resource="/" + app.config['CLOUD_STORAGE_BUCKET'] + "/" + filename,
            api_access_endpoint='https://storage.googleapis.com',
            expiration=timedelta(minutes=expiration)
        )
    return ""


def upload_file(file_stream, filename, content_type):
    client = storage.Client()
    bucket = client.bucket(app.config['CLOUD_STORAGE_BUCKET'])
    blob = bucket.blob(filename)

    blob.upload_from_string(
        file_stream,
        content_type=content_type
    )

    return filename


def get_cloud_storage_image_link(file_path, image):
    return upload_file(image.read(), file_path, image.mimetype)


def get_request_token(client_request):
    try:
        token = client_request.headers.get('token', None)
    except:
        token = None
    return token


def check_language_format(language):
    return language is not None and isinstance(language, str) and languages.get(alpha_2=language.lower()) is not None


def get_valid_number(object):
    if object is None or not isinstance(object, str):
        return None

    if len(object) == 1 and not match("^[0-9]$", object):
        return None

    if not match("^[1-9][0-9]*$", object):
        return None

    try:
        return int(object)
    except:
        return None


def translate_text(text, language):
    try:
        translate_client = translate.Client()
        translation = translate_client.translate(
            text,
            target_language=language
        )

        return translation['translatedText'], None

    except BadRequest:
        return None, get_response(status=HTTPStatus.BAD_REQUEST)
    except:
        return None, get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)


def translate_post(post, language):
    translated_post = dict()

    for field in ["title", "description"]:
        translate, response = translate_text(getattr(post, field, ""), language)
        if response is not None:
            return None, response
        translated_post[field] = translate

    return translated_post, None


def label_score(score):
    if score > 0.90:
        return "BEST"
    if score > 0.65:
        return "VERY GOOD"
    if score > 0.40:
        return "GOOD"
    if score > 0.20:
        return "POSITIVE"

    if score > -0.20:
        return "NEUTRAL"

    if score > -0.40:
        return "NEGATIVE"
    if score > -0.65:
        return "BAD"
    if score > -0.90:
        return "VERY BAD"
    if score >= -1.00:
        return "WORST"

    return ""


def analyze_text(text):
    try:
        client = language.LanguageServiceClient()
        document = gcl_types.Document(
            content=text,
            type=enums.Document.Type.PLAIN_TEXT
        )

        sentiment = client.analyze_sentiment(document=document).document_sentiment
        score = sentiment.score
    except BadRequest:
        return None, get_response(status=HTTPStatus.BAD_REQUEST)
    except:
        return None, get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)

    return label_score(score), None


def get_image_labels(vision_response):
    labels_dict = dict()
    labels = vision_response.label_annotations

    for label in labels:
        labels_dict[label.description] = label.score
    return labels_dict


def get_image_landmarks(vision_response):
    landmarks = vision_response.landmark_annotations
    landmarks_dict = dict()

    for landmark in landmarks:
        landmarks_dict[landmark.description] = []

        for location in landmark.locations:
            lat_lng = location.lat_lng
            landmarks_dict[landmark.description].append({
                "lat": lat_lng.latitude,
                "lon": lat_lng.longitude
            })

    return landmarks_dict


def analyze_image(path):
    path = "gs://" + app.config["CLOUD_STORAGE_BUCKET"] + "/" + path
    try:
        analyze = dict()
        client = ImageAnnotatorClient()
        image = gcv_types.Image()
        image.source.image_uri = path

        vision_response = client.label_detection(image=image)
        analyze["label"] = get_image_labels(vision_response)

        vision_response = client.landmark_detection(image=image)
        analyze["landmarks"] = list(get_image_landmarks(vision_response).keys())

        return analyze, None
    except:
        return None, get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)


def analyze_post(post):
    translated_post, response = translate_post(post, "en")
    if response is not None:
        return None, response

    analyzed_post = dict()
    for field in ["title", "description"]:
        analyze, response = analyze_text(translated_post[field])

        if response is not None:
            return None, response
        analyzed_post[field] = analyze

    analyze, response = analyze_image(post.link)
    if response is not None:
        return None, response

    analyzed_post["image"] = analyze
    return analyzed_post, None


def delete_cloud_storage_content(blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(app.config["CLOUD_STORAGE_BUCKET"])

    blob = bucket.blob(blob_name)
    blob.delete()


def delete_cloud_storage_folder(folder_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(app.config["CLOUD_STORAGE_BUCKET"])

    blobs = bucket.list_blobs(prefix=folder_name)
    for blob in blobs:
        blob.delete()


def object_to_dict(object, fields):
    obj_dict = dict()
    for field, _ in fields:
        try:
            obj_dict[field] = object[field]
        except:
            pass
    return obj_dict


def get_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def locate_post(post, query_data):
    path = "gs://" + app.config["CLOUD_STORAGE_BUCKET"] + "/" + post.link
    try:
        client = ImageAnnotatorClient()
        image = gcv_types.Image()
        image.source.image_uri = path

        vision_response = client.landmark_detection(image=image)
        landmarks = list(get_image_landmarks(vision_response).values())
        if len(landmarks) == 0:
            return None, get_response(status=HTTPStatus.NO_CONTENT)

        coordinates = landmarks[0]
        if len(coordinates) == 0:
            return None, get_response(status=HTTPStatus.NO_CONTENT)

        return {
                   "location": "https://maps.googleapis.com/maps/api/staticmap?center={},{}&zoom={}&size={}x{}&key={}".format(
                       coordinates[0]["lat"],
                       coordinates[0]["lon"],
                       str(query_data["zoom"]),
                       str(query_data["width"]),
                       str(query_data["height"]),
                       app.config["GOOGLE_MAPS_API_KEY"]
                   )
               }, None
    except:
        return None, get_response(status=HTTPStatus.INTERNAL_SERVER_ERROR)


def check_api_key(api_key):
    if api_key is None or not isinstance(api_key, str):
        return False

    try:
        keys = Keys.query.filter(Keys.api_key == get_hash(api_key)).all()
        if len(keys) == 0:
            return False

    except:
        return False
    return True


def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if check_api_key(request.headers.get('backend-api-key', None)):
            return view_function(*args, **kwargs)

        return get_response(status=HTTPStatus.UNAUTHORIZED)

    return decorated_function
