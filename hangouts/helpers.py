from django.forms.models import model_to_dict
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

import re

# ----------------------- send message asynchronously -----------------------#
def send_message(body, user):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'GDN Support Bot service key.json', scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    resp = chat.spaces().messages().create(parent=user, body=body).execute()


# def delete_message(name):
#     scopes = ['https://www.googleapis.com/auth/chat.bot']
#     credentials = ServiceAccountCredentials.from_json_keyfile_name(
#         'GDN Support Bot service key.json', scopes)
#     http = Http()
#     credentials.authorize(http)
#     chat = build('chat', 'v1', http=http)
#     resp = chat.spaces().messages().delete(name=name).execute()

def generate_fields_dict(work_item):
    model_dict = model_to_dict(work_item)

    key_filter = ["id", "workitem_ptr"]
    for key in list(model_dict):
        if key in key_filter:
            del model_dict[key]

    return model_dict


def create_url_of_work_item(work_item_object):
    name = type(work_item_object).__name__
    splitted = re.sub('(?!^)([A-Z][a-z]+)', r' \1', name).split()
    return "%20".join(splitted)
