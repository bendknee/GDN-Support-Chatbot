from django.db import models


class WorkItem(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    path_dict = {"title": "System.Title", "description": "System.Description"}


class HardwareSupport(WorkItem):
    hardware_type = models.CharField(max_length=30)
    severity = models.CharField(max_length=20, null=True)
    path_dict = dict(WorkItem.path_dict, **{"hardware_type": "Support.HardwareType",
                                            "severity": "Microsoft.VSTS.Common.Severity"})
    url = "Hardware%20Support"


class SoftwareSupport(WorkItem):
    requested_by = models.TextField()
    third_party = models.CharField(max_length=30)
    severity = models.CharField(max_length=20, null=True)
    path_dict = dict(WorkItem.path_dict, **{"third_party": "Support.3rdPartyApp",
                                            "requested_by": "Support.RequestedBy",
                                            "severity": "Microsoft.VSTS.Common.Severity"})
    url = "Software%20Support"


class WorkItemCreated(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)


class User(models.Model):
    name = models.CharField(max_length=40)
    work_item = models.OneToOneField(WorkItem, on_delete=models.SET_NULL, null=True)
    state = models.CharField(default='initial', max_length=30)
    final = models.BooleanField(default=False)
    jwt_token = models.CharField(max_length=700, null=True)
    refresh_token = models.CharField(max_length=750, null=True)

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