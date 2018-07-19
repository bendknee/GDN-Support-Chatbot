# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from hangouts.models import VstsArea

import hangouts.views

import base64
import json
import requests
import traceback

VSTS_PERSONAL_TOKEN = 'yhissyen5qljuutmcdesr3w3ov2saj6ujhsqnr7dskvkxa6rhq5a'
ENCODED_PAT = str(base64.b64encode(b':' + bytes(VSTS_PERSONAL_TOKEN, 'utf-8'))).replace("b'", '').replace("'", '')
BASE_URL = 'https://{{account_name}}.visualstudio.com/'
ACCOUNT_NAME = 'quickstartbot'


# ----------------------- post bug to VSTS -----------------------#
def create_bug(bug_dict, space):
    url = BASE_URL.replace("{{account_name}}", ACCOUNT_NAME) + '{{Project}}/_apis/wit/workitems/$Bug?api-version=4.1'
    headers = {'Authorization': 'Basic ' + ENCODED_PAT, "Content-Type": "application/json-patch+json"}
    payload = []

    for key, value in bug_dict.items():
        field = {
            "op": "add",
            "path": key,
            "value": value
        }
        payload.append(field)

    req = requests.post(url.replace("{{Project}}", "MyFirstProject"), headers=headers, data=json.dumps(payload))
    body = hangouts.views.generate_body(req.json())
    hangouts.views.send_message(body, space)


# ----------------------- receive webhook from VSTS -----------------------#
@csrf_exempt
def receive_webhook(request):
    try:
        event = json.loads(request.body)

        body = hangouts.views.generate_body(event['resource'])

        # get all spaces subscribed to area

        area = VstsArea.objects.get(name=event['resource']['fields']['System.AreaPath'])

        spaces = area.hangoutsSpaces.all()
        for space in spaces:
            hangouts.views.send_message(body, space.__str__())

        return JsonResponse({"text": "success!"}, content_type='application/json')

    except:
        traceback.print_exc()
        return JsonResponse({"text": "failed!"}, content_type='application/json')


def get_projects():
    project_list = set()
    url = BASE_URL.replace("{{account_name}}", ACCOUNT_NAME) + '_apis/projecthistory?api-version=4.1-preview.2'
    headers = {'Authorization': 'Basic ' + ENCODED_PAT}
    req = requests.get(url, headers=headers)
    response = req.json()
    for obj in response["value"]:
        project_list.add(obj["name"])
    return project_list


# ----------------------- get all areas from VSTS -----------------------#
def get_all_areas():
    areas_list = []
    url = BASE_URL.replace('{{account_name}}',
                           ACCOUNT_NAME) + '{{Project}}/_apis/wit/classificationnodes?api-version=4.1&$depth=99'
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
