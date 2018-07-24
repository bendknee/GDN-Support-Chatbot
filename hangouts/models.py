from django.db import models


class WorkItem(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()


class HardwareSupport(WorkItem):
    hardware_type = models.CharField(max_length=30)
    image = models.TextField(default="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/WMF-Agora-Settings_808080.svg/1024px-WMF-Agora-Settings_808080.svg.png", editable=False)


class SoftwareSupport(WorkItem):
    requested_by = models.CharField(max_length=30)
    third_party = models.CharField(max_length=30)
    image = models.TextField(default="")


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