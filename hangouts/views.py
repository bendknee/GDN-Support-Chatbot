# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .states import *
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from hangouts.models import User, HardwareSupport, SoftwareSupport
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials


import json

HANGOUTS_CHAT_API_TOKEN = 'SuCgaoGMzcA-U5xymm8khOEEezAapfV9fj5r2U3Tcjw='


# ----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receive_message(payload):
    event = json.loads(payload.body)
    print(event)
    if event['token'] == HANGOUTS_CHAT_API_TOKEN:
        user_object, created = User.objects.get_or_create(name=event['space']['name'])
        state = states_list[user_object.state]
        if event['type'] == 'ADDED_TO_SPACE' and event['space']['type'] == 'ROOM':
            message = 'Thanks for adding me to "%s"!' % event['space']['displayName']
            response = text_format(message)

        elif event['type'] == 'MESSAGE':
            # room or direct message
            if event['space']['type'] == 'ROOM':
                message = event['message']['argumentText'][1:]
            else:
                message = event['message']['argumentText']
            if state.is_waiting_text():
                response = state.action(message, event)
            else:
                response = text_format("Please complete above Card action first")

        elif event['type'] == 'CARD_CLICKED':
            if not state.is_waiting_text():
                # response can be text or card, depending on action
                response = handle_action(event)
        else:
            return
    else:
        return

    return JsonResponse(response, content_type='application/json')


def text_format(message):
    return {"text": message}


def handle_action(event):
    action = event['action']
    user_object = User.objects.get(event['space']['name'])
    state = states_list[user_object.state]
    if action['actionMethodName'] == "choose_type":
        response = state.action(action['parameters'][0]['value'], event)
    elif action['actionMethodName'] == "hardware_type":
        response = state.action(action['parameters'][0]['value'], event)
    elif action['actionMethodName'] == "software_type":
        response = state.action(action['parameters'][0]['value'], event)
    elif action['actionMethodName'] == "edit_work_item":
        response = state.action(action['parameters'][0]['value'], event)
    elif action['actionMethodName'] == "save_work_item":
        response = state.action(action['actionMethodName'], event)
    else:
        return

    change_state(event['space']['name'])
    return response



# ----------------------- send message asynchronously -----------------------#
def send_message(body, space):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'project-id-2458129994854391868-7fe6d3521132.json', scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    resp = chat.spaces().messages().create(parent=space, body=body).execute()

    print(resp)


# ----------------------- card generators -----------------------#
def generate_choices(title, list, method):
    if list == [] and method == 'unsubscribe':
        return text_format("You did not subscribe to any area.")

    card = {
        "cards": [
            {
                "header": {
                    "title": title
                },
                "sections": [
                    {
                        "widgets": [
                        ]
                    }
                ]
            }
        ]
    }

    for item in list:
        item_widget = {
            "keyValue": {
                "content": item,
                "onClick": {
                    "action": {
                        "actionMethodName": method,
                        "parameters": [
                            {
                                "key": "param",
                                "value": item
                            }
                        ]
                    }
                }
            }
        }

        card['cards'][0]['sections'][0]['widgets'].append(item_widget)

    return card

def generate_edit_work_item(work_item):
    dict = generate_fields_dict(work_item)
    for old_key in dict.keys():
        new_key = old_key.replace("_", " ").title()
        dict[new_key] = dict.pop(old_key)

    card = {
        "cards": [
            {
                "header": {
                    "title": work_item.title,
                    "imageUrl": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/WMF-Agora-Settings_808080.svg/1024px-WMF-Agora-Settings_808080.svg.png"
                },
                "sections": [
                    {
                        "widgets": [
                        ]
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "SAVE",
                                            "onClick": {
                                                "action": {
                                                    "actionMethodName": "save_work_item",
                                                }
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }


    for label, content in dict.items():
        item_widget = {
            "keyValue": {
                "topLabel": label,
                "content": content,
                "button": {
                    "textButton": {
                        "text": "Edit",
                        "onClick": {
                            "action": {
                                "actionMethodName": "edit_work_item",
                                "parameters": [
                                    {
                                        "key": "field",
                                        "value": label
                                    }
                                ]
                            }
                        }

                    }
                }
            }
        }

        card['cards'][0]['sections'][0]['widgets'].append(item_widget)

    return card

def generate_fields_dict(work_item):
    dict = model_to_dict(work_item)
    del dict["id"]

    return dict