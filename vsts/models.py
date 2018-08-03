from django.db import models
from hangouts.models import User


class CreatedWorkItems(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
