from django.db import models


class WorkItem(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    path_dict = {"title": "System.Title", "description": "System.Description"}


class HardwareSupport(WorkItem):
    hardware_type = models.CharField(max_length=30)
    severity = models.CharField(max_length=10)
    self_dict = {"hardware_type": "Support.HardwareType", "severity": "Microsoft.VSTS.Common.Severity"}
    path_dict = dict(WorkItem.path_dict, **self_dict)


class SoftwareSupport(WorkItem):
    requested_by = models.CharField(max_length=30)
    third_party = models.CharField(max_length=30)
    severity = models.CharField(max_length=10)
    self_dict = {"requested_by": "Ticketing.HardwareType", "severity": "Microsoft.VSTS.Common.Severity"}
    # path_dict = dict(WorkItem.path_dict, **self_dict)


class User(models.Model):
    name = models.CharField(max_length=40)
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, null=True)
    state = models.CharField(default='initial', max_length=30)

    def __str__(self):
        return self.name


class VstsArea(models.Model):
    name = models.CharField(max_length=30)
    hangoutsSpaces = models.ManyToManyField(User)

    def __str__(self):
        return self.name