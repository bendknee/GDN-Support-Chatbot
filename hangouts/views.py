# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .states import *
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from hangouts.models import User
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

import json


# ----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receive_message(payload):
    event = json.loads(payload.body)
    print(event)
    if event['token'] == settings.HANGOUTS_CHAT_API_TOKEN:
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
            if message == '/help':
                response = text_format('Type `/where` to know where you are on issuing a new Work Item\n'
                                       + 'Type `/reset` to abort all progress on issuing a new Work Item')
            elif message == '/reset':
                User.objects.filter(name=event['space']['name']).delete()
                response = text_format("Your progress has been aborted")
            elif message == '/where':
                response = text_format(state.where())
            elif state.is_waiting_text():
                response = state.action(message, event)
            else:
                response = text_format(state.where())

        elif event['type'] == 'CARD_CLICKED':
            if not state.is_waiting_text():
                # response can be text or card, depending on action
                action = event['action']
                user_object = User.objects.get(name=event['space']['name'])
                state = states_list[user_object.state]

                response = state.action(action['parameters'][0]['value'], event)
            else:
                response = {}
        else:
            return
    else:
        return

    return JsonResponse(response, content_type='application/json')


def text_format(message):
    return {"text": message}


# ----------------------- send message asynchronously -----------------------#
def send_message(body, user):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'GDN Support Bot service key.json', scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    resp = chat.spaces().messages().create(parent=user, body=body).execute()

    print(resp)


# ----------------------- card generators -----------------------#
def generate_choices(title, choices, method):
    if choices == [] and method == 'unsubscribe':
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

    for item in choices:
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
    temp_dict = generate_fields_dict(work_item)

    del temp_dict["title"]
    if "requested_by" in temp_dict:
        del temp_dict["requested_by"]

    work_item_dict = {}

    for old_key in temp_dict.keys():
        new_key = old_key.replace("_", " ").title()
        work_item_dict[new_key] = temp_dict[old_key]

    card = {
        "cards": [
            {
                "sections": [
                    {
                        "widgets": [
                            {
                                "keyValue": {
                                    "content": work_item.title,
                                    "iconUrl": "http://hangouts-vsts.herokuapp.com" +
                                               static('png/' + "hardware_support" + '.png'),
                                    "button": {
                                        "textButton": {
                                            "text": "Edit",
                                            "onClick": {
                                                "action": {
                                                    "actionMethodName": "edit_work_item",
                                                    "parameters": [
                                                        {
                                                            "key": "field",
                                                            "value": "Title"
                                                        }
                                                    ]
                                                }
                                            }

                                        }
                                    }
                                }
                            }
                        ]
                    },
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
                                                    "parameters": [
                                                        {
                                                            "key": "field",
                                                            "value": "save"
                                                        }
                                                    ]
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

    for label, content in work_item_dict.items():
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

        card['cards'][0]['sections'][1]['widgets'].append(item_widget)

    return card


def generate_updated_work_item(work_item):

    fields = {'Revised by': work_item['revisedBy']['name']}

    if 'System.State' in work_item['fields']:
        fields['State'] = 'Changed from `' + work_item['fields']['System.State']['oldValue'] + \
                          '` to `' + work_item['fields']['System.State']['newValue'] + '`'

    if 'System.History' in work_item['fields']:
        fields['Comment'] = work_item['fields']['System.History']['newValue']

    card = {
        "cards": [
            {
                "sections": [
                    {
                        "widgets": [
                            {
                                "keyValue": {
                                    "content": work_item['revision']['fields']['System.Title'],
                                    "iconUrl": "http://hangouts-vsts.herokuapp.com" +
                                               static('png/' + work_item['revision']['fields']['System.WorkItemType'] +
                                                      '.png')
                                }
                            }
                        ]
                    },
                    {
                        "widgets": [
                        ]
                    }
                ]
            }
        ]
    }

    for label, content in fields.items():
        item_widget = {
            "keyValue": {
                "topLabel": label,
                "content": content
            }
        }

        card['cards'][0]['sections'][1]['widgets'].append(item_widget)

    return card


def generate_fields_dict(work_item):
    dict = model_to_dict(work_item)

    del dict["id"]
    del dict["workitem_ptr"]

    return dict
