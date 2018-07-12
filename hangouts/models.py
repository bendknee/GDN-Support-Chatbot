from django.db import models

class HangoutsSpace(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class VstsArea(models.Model):
    name = models.CharField(max_length=30)
    hangoutsSpaces = models.ManyToManyField(HangoutsSpace)

    def __str__(self):
        return self.name