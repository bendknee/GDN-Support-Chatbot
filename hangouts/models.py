from datetime import datetime
from django.db import models


class WorkItem(models.Model):
    path_dict = {"title": "System.Title", "description": "System.Description"}

    title = models.CharField(max_length=50)
    description = models.TextField()
    saved_url = models.TextField(null=True)


class HardwareSupport(WorkItem):
    path_dict = dict(WorkItem.path_dict, **{"hardware_type": "Support.HardwareType",
                                            "severity": "Microsoft.VSTS.Common.Severity"})
    url = "Hardware%20Support"
    severities_list = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
    hardware_list = ["Internet/Wifi", "Laptop/Computer", "Mobile Device", "Other", "Printer"]

    hardware_type = models.CharField(choices=tuple((x, x) for x in hardware_list), max_length=30)
    severity = models.IntegerField(choices=tuple((int(x[0]), x) for x in severities_list),
                                   default=severities_list[2])


class SoftwareSupport(WorkItem):
    path_dict = dict(WorkItem.path_dict, **{"third_party": "Support.3rdPartyApp",
                                            "requested_by": "Support.RequestedBy",
                                            "severity": "Microsoft.VSTS.Common.Severity"})
    url = "Software%20Support"
    severities_list = ["1 - Critical", "2 - High", "3 - Medium", "4 - Low"]
    software_list = ["GSuite", "Power BI", "VSTS", "Fill your own.."]

    requested_by = models.TextField()
    third_party = models.CharField(max_length=30)
    severity = models.IntegerField(choices=tuple((int(x[0]), x) for x in severities_list),
                                   default=severities_list[2])


class User(models.Model):
    name = models.CharField(max_length=40)
    work_item = models.OneToOneField(WorkItem, on_delete=models.SET_NULL, null=True)
    state = models.CharField(max_length=30, default="initial")
    is_finished = models.BooleanField(default=False)
    jwt_token = models.CharField(max_length=700, null=True)
    refresh_token = models.CharField(max_length=750, null=True)
    last_auth = models.DateTimeField(default=datetime.now(), null=True)

    def __str__(self):
        return self.name

    def get_work_item(self):
        try:
            return self.work_item.hardwaresupport
        except HardwareSupport.DoesNotExist:
            pass
        try:
            return self.work_item.softwaresupport
        except SoftwareSupport.DoesNotExist:
            pass