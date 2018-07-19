# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from hangouts.models import VstsArea, HangoutsSpace, HardwareSupport, SoftwareSupport
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials

import vsts.views

import json

HANGOUTS_CHAT_API_TOKEN = 'SuCgaoGMzcA-U5xymm8khOEEezAapfV9fj5r2U3Tcjw='

#----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receive_message(request):
    global current_function
    event = json.loads(request.body)
    print(event)
    if event['token'] == HANGOUTS_CHAT_API_TOKEN:
        space_object, created = HangoutsSpace.objects.get_or_create(name=event['space']['name'])
        state = space_object.state
        if event['type'] == 'ADDED_TO_SPACE' and event['space']['type'] == 'ROOM':
            message = 'Thanks for adding me to "%s"!' % event['space']['displayName']
            response = text(message)

        elif event['type'] == 'MESSAGE':
            # room or direct message
            if event['space']['type'] == 'ROOM':
                message = event['message']['argumentText'][1:]
            else:
                message = event['message']['argumentText']

            response = current_function[state](message, event)

        elif event['type'] == 'CARD_CLICKED':
            # response can be text or card, depending on action
            response = handle_action(event)
        else:
            return
    else:
        return

    return JsonResponse(response, content_type='application/json')

def initial_state(message, event):
    if message.lower() == 'subscribe':
        response = generate_choices("Choose area", vsts.views.get_all_areas(), "subscribe")
    elif message.lower() == 'unsubscribe':
        response = generate_choices("Choose area", get_areas(event['space']['name']), "unsubscribe")
    elif message.lower() == 'support':
        response = generate_choices("Choose work item type", ["Hardware Support", "Software Support"], "support_type")
    else:
        message = 'You said: `%s`' % message
        response = text(message)

    return response

def text(message):
    return {"text": message}

def handle_action(event):
    action = event['action']
    if action['actionMethodName'] == "subscribe":
        response = text(subscribe(action['parameters'], event['space']))
    elif action['actionMethodName'] == "unsubscribe":
        response = text(unsubscribe(action['parameters'], event['space']))
    elif action['actionMethodName'] == "support_type":
        choose_support_type(action['parameters'][0]['value'], event['space'])
        response = text("Please enter title")
    elif action['actionMethodName'] == "hardware_type":
        response = set_hardware_type(action['parameters'][0]['value'], event['space'])
    else:
        return

    return response

#----------------------- create work item -----------------------#
def choose_support_type(type, space):
    if type == 'Hardware Support':
        hardware_object, created = HardwareSupport.objects.create(title='New')
        HangoutsSpace.objects.update_or_create(name=space['name'], state='hardware_title_state',
                                               hardware_support=hardware_object)
    elif type == 'Software Support':
        software_object, created = SoftwareSupport.objects.create(title='New')
        HangoutsSpace.objects.update_or_create(name=event['space']['name'], state='software_title_state',
                                               software_support=software_object)

def set_hardware_title(message, event):
    space_object, created = HangoutsSpace.objects.get_or_create(name=event['space']['name'])

    hardware_object = space_object.hardware_support
    hardware_object.title = message
    hardware_object.save()

    HangoutsSpace.objects.update_or_create(name=event['space']['name'], state='initial_state')  # update state
    hardware_type = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]
    response = generate_choices("Choose Hardware Type", hardware_type, "hardware_type")

    return response

def set_hardware_type(type, space):
    space_object, created = HangoutsSpace.objects.get_or_create(name=space['name'])

    hardware_object = space_object.hardware_support
    hardware_object.hardware_type = type
    hardware_object.save()

    HangoutsSpace.objects.update_or_create(name=space['name'], state='hardware_desc_state')  # update state
    response = text("Please enter description")

    return response

def set_hardware_description(message, event):
    space_object, created = HangoutsSpace.objects.get_or_create(name=event['space']['name'])

    hardware_object = space_object.hardware_support
    hardware_object.description = message
    hardware_object.save()

    HangoutsSpace.objects.update_or_create(name=event['space']['name'], state='initial_state')  # update state
    response = create_hardware_support()

    return response

def create_hardware_support():
    hardware_dict = {''}
    json_resp = vsts.views.create_work_item(hardware_dict)
    response = generate_hardware_support(json_resp)
    return response

#----------------------- send message asynchronously -----------------------#
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

#----------------------- subscribe or unsubscribe -----------------------#
def subscribe(parameters, space):
    area = parameters[0]['value']
    space = space['name']

    space_object, created = HangoutsSpace.objects.get_or_create(name=space) # get_or_create() returns tuple
    area_object, created = VstsArea.objects.get_or_create(name=area)
    area_object.hangoutsSpaces.add(space_object)

    return "Subscribed to area `%s`" % area

def unsubscribe(parameters, space):
    area = parameters[0]['value']
    space = space['name']

    space_object, created = HangoutsSpace.objects.get_or_create(name=space) # get_or_create() returns tuple
    area_object, created = VstsArea.objects.get_or_create(name=area)
    area_object.hangoutsSpaces.remove(space_object)

    return "Unsubscribed to area `%s`" % area

#----------------------- get areas -----------------------#
def get_areas(space):
    space_object = HangoutsSpace.objects.get(name=space)
    areas = space_object.vstsarea_set.all()
    areas_list = [area.__str__() for area in areas]
    return areas_list

#----------------------- card generators -----------------------#
def generate_choices(title, list, method):
    if list == [] and method == 'unsubscribe':
        return text("You did not subscribe to any area.")

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

current_function = {"initial_state": initial_state, "hardware_title_state": set_hardware_title, "hardware_description_state": set_hardware_description}