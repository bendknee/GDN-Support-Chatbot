from django.db import models


class WorkItem(models.Model):
    title = models.CharField(null=False, max_length=50)
    description = models.TextField()


class HardwareSupport(WorkItem):
    hardware_type = models.CharField(max_length=30)


class SoftwareSupport(WorkItem):
    requested_by = models.CharField(max_length=30)
    third_party = models.CharField(max_length=30)


class User(models.Model):
    name = models.CharField(max_length=30)
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE)
    state = models.CharField(default='initial_state', max_length=30)

    def __str__(self):
        return self.name


class VstsArea(models.Model):
    name = models.CharField(max_length=30)
    hangoutsSpaces = models.ManyToManyField(User)

    def __str__(self):
        return self.name