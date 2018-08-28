# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import CreatedWorkItems
from hangouts.cards import generate_updated_work_item, text_format
from hangouts.helpers import send_message
from hangouts.models import User

from datetime import datetime, timezone

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import json
import requests
import traceback


# ----------------------- post work item to VSTS -----------------------#
def create_work_item(work_item_dict, url, user):
    url = 'https://quickstartbot.visualstudio.com/' + 'Support/_apis/wit/workitems/$' + url + '?api-version=4.1'
    headers = {'Authorization': 'Bearer ' + user.jwt_token, "Content-Type": "application/json-patch+json"}
    payload = []

    for key, value in work_item_dict.items():
        field = {
            "op": "add",
            "path": "/fields/" + key,
            "value": value
        }
        payload.append(field)

    req = requests.post(url, headers=headers, data=json.dumps(payload))

    CreatedWorkItems.objects.create(id=req.json()['id'], user=user)

    return req.json()


# ----------------------- receive webhook from VSTS -----------------------#
@csrf_exempt
def notification(payload):
    try:
        event = json.loads(payload.body)

        body = generate_updated_work_item(event['resource'])

        work_item = CreatedWorkItems.objects.get(id=event['resource']['workItemId'])

        send_message(text_format("`NOTIFICATION`"), work_item.user.name)
        send_message(text_format("Your Work Item has been updated:"), work_item.user.name)
        send_message(body, work_item.user.name)

        return JsonResponse({"text": "success!"}, content_type='application/json')

    except:
        traceback.print_exc()
        return JsonResponse({"text": "failed!"}, content_type='application/json')


# ----------------------- authorize VSTS -----------------------#
@csrf_exempt
def authorize(payload):
    try:
        code = payload.GET.get('code')
        user_pk = payload.GET.get('state')

        url = "https://app.vssps.visualstudio.com/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {"client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": settings.VSTS_OAUTH_SECRET,
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": code,
                "redirect_uri": settings.WEBHOOK_URL + "/api/vsts/oauth"}
        response = requests.post(url, headers=headers, data=body).json()

        user_object = User.objects.get(pk=int(user_pk))
        user_object.jwt_token = response["access_token"]
        user_object.refresh_token = response["refresh_token"]
        user_object.last_auth = datetime.now(timezone.utc)
        user_object.save()

        body = text_format("Sign in successful. Type `support` to begin issuing new Work Item.")
        send_message(body, user_object.name)

        return render(payload, "oauth_callback.html")

    except:
        traceback.print_exc()
        return HttpResponse("Fail.", content_type='application/json')


def token_expired_or_refresh(user_object):
    delta = datetime.now(timezone.utc) - user_object.last_auth
    if delta.seconds >= settings.VSTS_EXPIRY_TIME:
        url = "https://app.vssps.visualstudio.com/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {"client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": settings.VSTS_OAUTH_SECRET,
                "grant_type": "refresh_token",
                "assertion": user_object.refresh_token,
                "redirect_uri": settings.WEBHOOK_URL + "/api/vsts/oauth"}
        response = requests.post(url, headers=headers, data=body).json()

        user_object.jwt_token = response["access_token"]
        user_object.refresh_token = response["refresh_token"]
        user_object.last_auth = datetime.now(timezone.utc)
        user_object.save()
