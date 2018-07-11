# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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

            message = 'You said: `%s`' % message
            response = text(message)

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
                                            "text": "One",
                                            "onClick": {
                                                "action": {
                                                    "actionMethodName": "choose",
                                                    "parameters": [
                                                        {
                                                            "key": "number",
                                                            "value": "1"
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    },
                                    {
                                        "textButton": {
                                            "text": "Two",
                                            "onClick": {
                                                "action": {
                                                    "actionMethodName": "choose",
                                                    "parameters": [
                                                        {
                                                            "key": "number",
                                                            "value": "2"
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