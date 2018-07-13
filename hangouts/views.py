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


#----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receive_message(request):
    event = json.loads(request.body)
    print(event)
    if event['token'] == 'SuCgaoGMzcA-U5xymm8khOEEezAapfV9fj5r2U3Tcjw=':
        if event['type'] == 'ADDED_TO_SPACE' and event['space']['type'] == 'ROOM':
            message = 'Thanks for adding me to "%s"!' % event['space']['displayName']
            response = text(message)

        elif event['type'] == 'MESSAGE':
            if event['space']['type'] == 'ROOM':
                message = event['message']['argumentText'][1:]
            else:
                message = event['message']['argumentText']

            if message.lower() == 'subscribe':
                response = areas_response(vsts.views.get_all_areas(), "subscribe")
                print(response)
            elif message.lower() == 'unsubscribe':
                response = areas_response(get_areas(event['space']['name']), "unsubscribe")
                print(response)
            else:
                message = 'You said: `%s`' % message
                response = text(message)

        elif event['type'] == 'CARD_CLICKED':
            # response can be text or card, depending on action
            response = handle_action(event)


        else:
            return
    else:
        return

    return JsonResponse(response, content_type='application/json')

def text(message):
    response = {"text": message}
    return response

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
                    "title": message['resource']['fields']['System.Title'],
                    "subtitle": "created by " + message['resource']['fields']['System.CreatedBy'],
                    "imageUrl": "https://www.iconspng.com/uploads/bad-bug/bad-bug.png"
                  },
                  "sections": [
                    {
                      "widgets": [
                          {
                              "keyValue": {
                                  "topLabel": "Area Path",
                                  "content": message['resource']['fields']['System.AreaPath']
                              }
                          },
                          {
                              "keyValue": {
                                  "topLabel": "Priority",
                                  "content": message['resource']['fields']['Microsoft.VSTS.Common.Severity']
                              }
                          },
                          {
                              "keyValue": {
                                  "topLabel": "Repro Steps",
                                  "content": message['resource']['fields']['Microsoft.VSTS.TCM.ReproSteps']
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
                                        "url": message['resource']['_links']['html']['href']
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