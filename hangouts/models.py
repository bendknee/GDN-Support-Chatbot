from django.db import models

class HangoutsSpace(models.Model):
    name = models.CharField(max_length=30)

class VstsArea(models.Model):
    name = models.CharField(max_length=30)
    hangoutsSpaces = models.ManyToManyField(HangoutsSpace)