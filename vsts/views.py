# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from hangouts.models import WorkItemCreated

import hangouts.views

import base64
import json
import requests
import traceback

ENCODED_PAT = str(base64.b64encode(b':' + bytes(settings.VSTS_PERSONAL_ACCESS_TOKEN,
                                                'utf-8'))).replace("b'", '').replace("'", '')


# ----------------------- post bug to VSTS -----------------------#
def create_work_item(work_item_dict, url, user):
    url = settings.VSTS_BASE_URL + 'Support/_apis/wit/workitems/$' + url + '?api-version=4.1'
    headers = {'Authorization': 'Basic ' + ENCODED_PAT, "Content-Type": "application/json-patch+json"}
    payload = []

    for key, value in work_item_dict.items():
        field = {
            "op": "add",
            "path": "/fields/" + key,
            "value": value
        }
        payload.append(field)

    req = requests.post(url, headers=headers, data=json.dumps(payload))

    WorkItemCreated.objects.create(id=req.json()['id'], user=user)


# ----------------------- receive webhook from VSTS -----------------------#
@csrf_exempt
def receive_webhook(request):
    try:
        event = json.loads(request.body)
        print(event)

        body = hangouts.views.generate_updated_work_item(event['resource'])

        work_item = WorkItemCreated.objects.get(id=event['resource']['workItemId'])

        hangouts.views.send_message(body, work_item.user.name)

        return JsonResponse({"text": "success!"}, content_type='application/json')

    except:
        traceback.print_exc()
        return JsonResponse({"text": "failed!"}, content_type='application/json')


def get_projects():
    project_list = set()
    url = settings.VSTS_BASE_URL + '_apis/projecthistory?api-version=4.1-preview.2'
    headers = {'Authorization': 'Basic ' + ENCODED_PAT}
    req = requests.get(url, headers=headers)
    response = req.json()
    for obj in response["value"]:
        project_list.add(obj["name"])
    return project_list


# ----------------------- get all areas from VSTS -----------------------#
def get_all_areas():
    areas_list = []
    url = settings.VSTS_BASE_URL + '{{Project}}/_apis/wit/classificationnodes?api-version=4.1&$depth=99'
    headers = {'Authorization': 'Basic ' + ENCODED_PAT}
    for project in get_projects():
        req = requests.get(url.replace("{{Project}}", project), headers=headers)
        response = req.json()
        try:
            for obj in response["value"]:
                if obj["structureType"] == "area":
                    areas_list += recursive_path_maker(obj)
        except KeyError:
            continue
    return areas_list


def recursive_path_maker(area, parent_path='', areas_list=None):
    if areas_list is None:
        areas_list = []
    if area["hasChildren"]:
        if parent_path != '':
            areas_list.append((parent_path + area["name"]))
        for child in area["children"]:
            recursive_path_maker(child, parent_path + area["name"] + "\\", areas_list)
    else:
        areas_list.append((parent_path + area["name"]))
    return areas_list


# ----------------------- authorize VSTS -----------------------#
@csrf_exempt
def authorize(request):
    try:
        code = request.GET.get('code')
        user_pk = request.GET.get('state')

        print(code)
        print(user_pk)

        return JsonResponse({"text": "success!"}, content_type='application/json')

    except:
        traceback.print_exc()
        return JsonResponse({"text": "failed!"}, content_type='application/json')

def isTokenRefresh():
    return False

def refreshToken():
    return