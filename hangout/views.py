# -*- coding: utf-8 -*- 
from __future__ import unicode_literals 

from django.shortcuts import render 
import json 
from django.http import HttpResponse, JsonResponse 
from django.views.decorators.csrf import csrf_exempt 
import requests 


@csrf_exempt 
def hello(request): 
    print(request.META)
    body_unicode = request.body.decode('utf-8')
    event = json.loads(body_unicode)
    if event['token'] == 'SuCgaoGMzcA-U5xymm8khOEEezAapfV9fj5r2U3Tcjw=':
        if event['type'] == 'ADDED_TO_SPACE' and event['space']['type'] == 'ROOM':
            text = 'Thanks for adding me to "%s"!' % event['space']['displayName']
        elif event['type'] == 'MESSAGE':
            text = 'You said: `%s`' % event['message']['text']
        else:
            return
    else:
        return
    return JsonResponse({"text": text}, content_type='application/json')
# 
# def hello(request): 
# payload = {'text': 'bro!!'} 
# url = "https://chat.googleapis.com/v1/spaces/gYb-1AAAAAE/messages" 
# requests.post(url, data=payload) 
# return JsonResponse({"nothing": "nothing"})