# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from hangouts.models import VstsArea
from hangouts.views import generateBody, sendMessage

import json
import requests
import traceback

VSTS_PERSONAL_ACCESS_TOKEN = 'OjIzcml2YWtzbml0NzRhaDNxd29pemlpNTZud2g0cnN5NHJqZXV1ZXBudzdlN29ocjVjc3E='

#----------------------- receive webhook from VSTS -----------------------#
@csrf_exempt
def receiveWebhook(request):
    try:
        event = json.loads(request.body)

        body = generateBody(event)

        # get all spaces subscribed to area

        area = VstsArea.objects.get(name=event['resource']['fields']['System.AreaPath'])

        spaces = area.hangoutsSpaces.all()
        for space in spaces:
            sendMessage(body, space.__str__())

        return JsonResponse({"text": "success!"}, content_type='application/json')

    except:
        traceback.print_exc()
        return JsonResponse({"text": "failed!"}, content_type='application/json')

def getProjects():
    project_list = set()
    url = 'https://gramediadigital.visualstudio.com/_apis/projecthistory?api-version=4.1-preview.2'
    headers = {'Authorization', 'Basic ' + VSTS_PERSONAL_ACCESS_TOKEN}
    req = requests.get(url, headers=headers)
    response = json.loads(req.json())
    for obj in response["value"]:
        project_list.add(obj["name"])
    return project_list

#----------------------- get all areas from VSTS -----------------------#
def getAreas():
    areas_list = []
    url = 'https://gramediadigital.visualstudio.com/{{Project}}/_apis/wit/classificationnodes?api-version=4.1&$depth=99'
    headers = {'Authorization', 'Basic ' + VSTS_PERSONAL_ACCESS_TOKEN}
    for project in getProjects():
        req = requests.get(url.replace("{{Project}}", project), headers=headers)
        response = json.loads(req.json())
        for obj in response["value"]:
            if obj["structureType"] == "area":
                areas_list += recursive_area(obj, areas_list=areas_list)

    return areas_list

def recursive_area(area, parent_path='', areas_list=[]):
    if area["hasChildren"]:
        if parent_path != '':
            areas_list.append((parent_path + area["name"]))
        for child in area["children"]:
            recursive_area(child, parent_path + area["name"] + "\\", areas_list)
    else:
        areas_list.append((parent_path + area["name"]))
    return areas_list

