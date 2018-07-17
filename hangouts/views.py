# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from hangouts.models import VstsArea, HangoutsSpace
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

import vsts.views

import json

HANGOUTS_CHAT_API_TOKEN = 'SuCgaoGMzcA-U5xymm8khOEEezAapfV9fj5r2U3Tcjw='

#----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receive_message(request):
    event = json.loads(request.body)
    print(event)
    if event['token'] == HANGOUTS_CHAT_API_TOKEN:
        if event['type'] == 'ADDED_TO_SPACE' and event['space']['type'] == 'ROOM':
            message = 'Thanks for adding me to "%s"!' % event['space']['displayName']
            response = text(message)

        elif event['type'] == 'MESSAGE':
            response = current_function(event)

        elif event['type'] == 'CARD_CLICKED':
            # response can be text or card, depending on action
            response = handle_action(event)

        else:
            return
    else:
        return

    return JsonResponse(response, content_type='application/json')


def initial_state(event):
    global current_function
    message = event['message']['argumentText']
    if event['space']['type'] == 'ROOM':
        message = message[1:]

    if message.lower() == 'subscribe':
        current_function = initial_state
        return areas_response(vsts.views.get_all_areas(), "subscribe")
    elif message.lower() == 'unsubscribe':
        current_function = initial_state
        return areas_response(get_areas(event['space']['name']), "unsubscribe")
    elif message.lower() == 'bug':
        message = 'Title:'
        current_function = title_state
        return text(message)
    else:
        current_function = initial_state
        message = 'You said: `%s`' % message
        return text(message)

def title_state(event):
    message = event['message']['argumentText']
    if event['space']['type'] == 'ROOM':
        message = message[1:]
    global current_function
    current_function = initial_state
    return text('Your title: ' + message)

def text(message):
    return {"text": message}

def handle_action(event):
    action = event['action']
    if action['actionMethodName'] == "subscribe":
        # response as text
        response = text(subscribe(action['parameters'], event['space']))
    elif action['actionMethodName'] == "unsubscribe":
        response = text(unsubscribe(action['parameters'], event['space']))
    else:
        return

    return response

def subscribe(parameters, space):
    area = parameters[0]['value']
    space = space['name']

    space_object, created = HangoutsSpace.objects.get_or_create(name=space) # get_or_create() returns tuple
    area_object, created = VstsArea.objects.get_or_create(name=area)
    area_object.hangoutsSpaces.add(space_object)

    return "Subscribed to area " + area

def unsubscribe(parameters, space):
    area = parameters[0]['value']
    space = space['name']

    space_object, created = HangoutsSpace.objects.get_or_create(name=space) # get_or_create() returns tuple
    area_object, created = VstsArea.objects.get_or_create(name=area)
    area_object.hangoutsSpaces.remove(space_object)

    return "Unsubscribed to area " + area

def get_areas(space):
    space_object = HangoutsSpace.objects.get(name=space)
    areas = space_object.vstsarea_set.all()
    areas_list = [area.__str__() for area in areas]
    return areas_list

def areas_response(areas_list, method):
    if areas_list == []:
        return text("You did not subscribe to any area.")

    card = {
        "cards": [
            {
                "header": {
                    "title": "Choose area"
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

    for area in areas_list:
        area_widget = {
            "keyValue": {
                "content": area,
                "onClick": {
                    "action": {
                        "actionMethodName": method,
                        "parameters": [
                            {
                                "key": "area",
                                "value": area
                            }
                        ]
                    }
                }
            }
        }

        card['cards'][0]['sections'][0]['widgets'].append(area_widget)

    return card

def send_message(body, space):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'project-id-2458129994854391868-7fe6d3521132.json', scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    body = body
    resp = chat.spaces().messages().create(
        parent=space,
        body=body).execute()

    print(resp)

def generate_body(message):
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


current_function = initial_state
bug_dict = {'/fields/System.Title': 'Titlenya', '/fields/Microsoft.VSTS.TCM.ReproSteps': 'Reprostepsnya'}