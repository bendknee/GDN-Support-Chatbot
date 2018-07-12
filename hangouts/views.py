# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from hangouts.models import VstsArea, HangoutsSpace
import json


#----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receiveMessage(request):
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

            if message == 'Subscribe':
                response = cards()
            else:
                message = 'You said: `%s`' % message
                response = text(message)

        elif event['type'] == 'CARD_CLICKED':
            # response can be text or card, depending on action
            response = handleAction(event)


        else:
            return
    else:
        return

    return JsonResponse(response, content_type='application/json')

def text(message):
    response = {"text": message}
    return response

def cards():
    response = {
        "cards": [
            {
                "header": {
                    "title": "Choose number!"
                },
                "sections": [
                    {
                        "widgets": [
                            {
                                "buttons": [
                                    {
                                        "textButton": {
                                            "text": "MyFirstProject\\team 2",
                                            "onClick": {
                                                "action": {
                                                    "actionMethodName": "chooseArea",
                                                    "parameters": [
                                                        {
                                                            "key": "area",
                                                            "value": "MyFirstProject\\team 2"
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "textButton": {
                                            "text": "MyFirstProject\\other area",
                                            "onClick": {
                                                "action": {
                                                    "actionMethodName": "chooseArea",
                                                    "parameters": [
                                                        {
                                                            "key": "area",
                                                            "value": "MyFirstProject\\other area"
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
    return response

def handleAction(event):
    action = event['action']
    if action['actionMethodName'] == "chooseArea":
        # response as text
        response = text(chooseArea(action['parameters'], event['space']))
    else:
        return

    return response


def chooseArea(parameters, space):
    area = parameters[0]['value']
    space = space['name']

    spaceObject, created = HangoutsSpace.objects.get_or_create(name=space)
    areaObject, created = VstsArea.objects.get_or_create(name=area)
    areaObject.hangoutsSpaces.add(spaceObject)

    return "Subscribed to area " + area