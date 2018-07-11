# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from httplib2 import Http
import json
from oauth2client.service_account import ServiceAccountCredentials


#----------------------- receive webhook from VSTS -----------------------#
@csrf_exempt
def receiveWebhook(request):
    event = json.loads(request.body)
    print(event)
    sendMessage(event)
    return JsonResponse({"text": "success!"}, content_type='application/json')

def sendMessage(message):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'project-id-2458129994854391868-7fe6d3521132.json', scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
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
    resp = chat.spaces().messages().create(
        parent='spaces/AAAAxvB-jOA',
        body=body).execute()
