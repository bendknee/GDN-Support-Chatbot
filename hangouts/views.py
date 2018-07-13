# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.sites import requests
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

            if message.lower() == 'Subscribe'.lower():
                response = allAreasCard(getAreas())
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

    spaceObject, created = HangoutsSpace.objects.get_or_create(name=space) # get_or_create() returns tuple
    areaObject, created = VstsArea.objects.get_or_create(name=area)
    areaObject.hangoutsSpaces.add(spaceObject)

    return "Subscribed to area " + area

#----------------------- get all areas from VSTS -----------------------#
def getAreas():
    # r = requests.get('https://api.github.com/events')
    # areas_json = r.json()

    areas_list = ['MyFirstProject\\team 2', 'MyFirstProject\\other area']

    return areas_list

def allAreasCard(areas_list):
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

    # card = json.loads(response)
    for area in areas_list:
        area_widget = {
                        "keyValue": {
                            "content": area,
                            "onClick": {
                                "action": {
                                    "actionMethodName": "chooseArea",
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

        # area_widget = json.loads(area_widget)
        card['cards']['sections']['widgets'].append(area_widget)

    return json.dumps(card)
