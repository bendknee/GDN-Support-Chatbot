from django.db import models


class HardwareSupport(models.Model):
    title = models.CharField
    hardware_type = models.CharField
    description = models.CharField


class SoftwareSupport(models.Model):
    requested_by = models.CharField
    third_party = models.CharField

class HangoutsSpace(models.Model):
    name = models.CharField(max_length=30)
    hardware_support = models.ForeignKey(HardwareSupport, on_delete=models.CASCADE, null=True)
    software_support = models.ForeignKey(SoftwareSupport, on_delete=models.CASCADE, null=True)
    state = models.CharField

    def __str__(self):
        return self.name

class VstsArea(models.Model):
    name = models.CharField(max_length=30)
    hangoutsSpaces = models.ManyToManyField(HangoutsSpace)

    def __str__(self):
        return self.name