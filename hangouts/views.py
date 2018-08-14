# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .cards import text_format
from .models import User
from .states import InitialState, states_list

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json


# ----------------------- receive message from Hangouts -----------------------#
@csrf_exempt
def receive_message(payload):
    event = json.loads(payload.body)
    print(event)
    if event['token'] == settings.HANGOUTS_CHAT_API_TOKEN:
        user_object, created = User.objects.get_or_create(name=event['space']['name'])
        state = states_list[user_object.state]
        if event['type'] == 'ADDED_TO_SPACE':
            response = text_format('Type `support` to start issuing new Work Item!\n\n'
                                   + 'Type `/where` to know where you are on issuing a new Work Item\n'
                                   + 'Type `/reset` to abort all progress on issuing a new Work Item\n'
                                   + 'Type `/help` to see available commands')

        elif event['type'] == 'MESSAGE':
            # room or direct message
            if event['space']['type'] == 'ROOM':
                message = event['message']['argumentText'][1:]
            else:
                message = event['message']['argumentText']
            if message == '/help':
                response = text_format('Type `support` to start issuing new Work Item!\n\n'
                                       + 'Type `/where` to know where you are on issuing a new Work Item\n'
                                       + 'Type `/reset` to abort all progress on issuing a new Work Item\n'
                                       + 'Type `/help` to see available commands')
            elif message == '/reset':
                user_object.is_finished = False
                user_object.state = InitialState.STATE_LABEL
                user_object.save()

                try:
                    user_object.work_item.delete()
                except AttributeError:
                    pass

                response = text_format("Your progress has been aborted")
            elif message == '/where':
                response = text_format(state.where())
            elif state.is_waiting_text():
                response = state.action(user_object, message, event)
            else:
                response = text_format(state.where())

        elif event['type'] == 'CARD_CLICKED':
            if not state.is_waiting_text():
                # response can be text or card, depending on action
                action = event['action']
                if action['actionMethodName'] == state.STATE_LABEL:
                    response = state.action(user_object, action['parameters'][0]['value'], event)
                else:
                    response = text_format(state.where())
            else:
                response = text_format(state.where())
        else:
            return
    else:
        return

    return JsonResponse(response, content_type='application/json')