# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import CreatedWorkItems
from base64 import b64encode
from datetime import datetime, timezone
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from hangouts import views as hangouts
from hangouts.models import User

import json
import requests
import traceback

ENCODED_PAT = str(b64encode(b':' + bytes(settings.VSTS_PERSONAL_ACCESS_TOKEN,
                                                'utf-8'))).replace("b'", '').replace("'", '')


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


# ----------------------- receive webhook from VSTS -----------------------#
@csrf_exempt
def notification(request):
    try:
        event = json.loads(request.body)
        print(event)

        body = hangouts.generate_updated_work_item(event['resource'])

        work_item = CreatedWorkItems.objects.get(id=event['resource']['workItemId'])

        hangouts.send_message(body, work_item.user.name)

        return JsonResponse({"text": "success!"}, content_type='application/json')

    except:
        traceback.print_exc()
        return JsonResponse({"text": "failed!"}, content_type='application/json')


# ----------------------- authorize VSTS -----------------------#
@csrf_exempt
def authorize(request):
    try:
        code = request.GET.get('code')
        user_pk = request.GET.get('state')

        url = "https://app.vssps.visualstudio.com/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {"client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": settings.VSTS_OAUTH_SECRET,
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": code,
                "redirect_uri": "https://hangouts-vsts.herokuapp.com/vsts/oauth"}
        response = requests.post(url, headers=headers, data=body).json()

        user_object = User.objects.get(pk=int(user_pk))
        user_object.jwt_token = response["access_token"]
        user_object.refresh_token = response["refresh_token"]
        user_object.last_auth = datetime.now(timezone.utc)
        user_object.save()

        print(code)
        print(user_pk)

        return HttpResponse("Sign in successful!")

    except:
        traceback.print_exc()
        return JsonResponse({"text": "failed!"}, content_type='application/json')


def token_expired_or_refresh(user_object):
    delta = datetime.now(timezone.utc) - user_object.last_auth
    if delta.seconds >= settings.VSTS_EXPIRY_TIME:
        url = "https://app.vssps.visualstudio.com/oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        body = {"client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": settings.VSTS_OAUTH_SECRET,
                "grant_type": "refresh_token",
                "assertion": user_object.refresh_token,
                "redirect_uri": "https://hangouts-vsts.herokuapp.com/vsts/oauth"}
        response = requests.post(url, headers=headers, data=body).json()

        user_object.jwt_token = response["access_token"]
        user_object.refresh_token = response["refresh_token"]
        user_object.last_auth = datetime.now(timezone.utc)
        user_object.save()

# def get_projects():
#     project_list = set()
#     url = settings.VSTS_BASE_URL + '_apis/projecthistory?api-version=4.1-preview.2'
#     headers = {'Authorization': 'Basic ' + ENCODED_PAT}
#     req = requests.get(url, headers=headers)
#     response = req.json()
#     for obj in response["value"]:
#         project_list.add(obj["name"])
#     return project_list


# ----------------------- get all areas from VSTS -----------------------#
# def get_all_areas():
#     areas_list = []
#     url = settings.VSTS_BASE_URL + '{{Project}}/_apis/wit/classificationnodes?api-version=4.1&$depth=99'
#     headers = {'Authorization': 'Basic ' + ENCODED_PAT}
#     for project in get_projects():
#         req = requests.get(url.replace("{{Project}}", project), headers=headers)
#         response = req.json()
#         try:
#             for obj in response["value"]:
#                 if obj["structureType"] == "area":
#                     areas_list += recursive_path_maker(obj)
#         except KeyError:
#             continue
#     return areas_list
