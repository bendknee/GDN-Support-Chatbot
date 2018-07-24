from django.db import models


class WorkItem(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    path_dict = {"title": "System.Title", "description": "System.Description", "severity": "Microsoft.VSTS.Common.Severity"}


class HardwareSupport(WorkItem):
    hardware_type = models.CharField(max_length=30)
    path_dict = dict(WorkItem.path_dict, **{"hardware_type": "Ticketing.HardwareType"})


class SoftwareSupport(WorkItem):
    requested_by = models.CharField(max_length=30)
    third_party = models.CharField(max_length=30)
    # path_dict = dict(WorkItem.path_dict, **{"requested_by": "Ticketing.HardwareType"})


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