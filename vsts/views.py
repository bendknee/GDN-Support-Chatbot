# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from hangouts.models import VstsArea, HangoutsSpace
from httplib2 import Http
import json
from oauth2client.service_account import ServiceAccountCredentials
import traceback


#----------------------- receive webhook from VSTS -----------------------#
@csrf_exempt
def receiveWebhook(request):
    try:
        event = json.loads(request.body)
        print("here")
        print(event)

        body = generateBody(event)

        # get all spaces subscribed to area

        area = VstsArea.objects.get(name=event['resource']['fields']['System.AreaPath'])


        spaces = area.hangoutsSpaces.all()
        print("all spaces:")
        print(spaces)

        for space in spaces:
            print("each space")
            print(space)
            sendMessage(body, space)

        return JsonResponse({"text": "success!"}, content_type='application/json')

    except:
        traceback.print_exc()
        return JsonResponse({"text": "failed!"}, content_type='application/json')

def sendMessage(body, space):
    print("masuk sendmessage")
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

def generateBody(message):
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
                                  "topLabel": "Priority",
                                  "content": str(message['resource']['fields']['Microsoft.VSTS.Common.Priority'])
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