# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .states import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from hangouts.models import User, HardwareSupport, SoftwareSupport
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

import vsts.views

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
            if message == '/help':
                response = text_format('Type "%s" to know where you are on issuing a new Work Item\n' % '/where'
                                       + 'Type "%s" to abort all progress on issuing a new Work Item' % '/reset')
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


def generate_bug(message):
    body = {
        "cards": [
            {
                "header": {
                    "title": message['fields']['System.Title'],
                    "subtitle": "created by " + message['fields']['System.CreatedBy'],
                    "imageUrl": "https://www.iconspng.com/uploads/bad-bug/bad-bug.png"
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "keyValue": {
                                    "topLabel": "Area Path",
                                    "content": message['fields']['System.AreaPath']
                                }
                            },
                            {
                                "keyValue": {
                                    "topLabel": "Severity",
                                    "content": message['fields']['Microsoft.VSTS.Common.Severity']
                                }
                            },
                            {
                                "keyValue": {
                                    "topLabel": "Repro Steps",
                                    "content": message['fields']['Microsoft.VSTS.TCM.ReproSteps']
                                }
                            }

                        ]
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "MORE",
                                            "onClick": {
                                                "openLink": {
                                                    "url": message['_links']['html']['href']
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
    return body


def generate_hardware_support(message):
    body = {
        "cards": [
            {
                "header": {
                    "title": message['fields']['System.Title'],
                    "subtitle": "created by " + message['fields']['System.CreatedBy'],
                    "imageUrl": "https://www.iconspng.com/uploads/bad-bug/bad-bug.png"
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "keyValue": {
                                    "topLabel": "Area Path",
                                    "content": message['fields']['System.AreaPath']
                                }
                            },
                            {
                                "keyValue": {
                                    "topLabel": "Severity",
                                    "content": message['fields']['Microsoft.VSTS.Common.Severity']
                                }
                            },
                            {
                                "keyValue": {
                                    "topLabel": "Repro Steps",
                                    "content": message['fields']['Microsoft.VSTS.TCM.ReproSteps']
                                }
                            }

                        ]
                    },
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "MORE",
                                            "onClick": {
                                                "openLink": {
                                                    "url": message['_links']['html']['href']
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
    return body
