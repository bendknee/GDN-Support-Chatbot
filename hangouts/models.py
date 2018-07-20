from django.db import models


class WorkItem(models.Model):
    title = models.CharField(null=False)
    description = models.TextField()


class HardwareSupport(WorkItem):
    hardware_type = models.CharField()


class SoftwareSupport(WorkItem):
    requested_by = models.CharField()
    third_party = models.CharField()


class User(models.Model):
    name = models.CharField(max_length=30)
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, null=False)
    state = models.CharField(default='initial_state')

    def __str__(self):
        return self.name


class VstsArea(models.Model):
    name = models.CharField(max_length=30)
    hangoutsSpaces = models.ManyToManyField(User)

    def __str__(self):
        return self.name