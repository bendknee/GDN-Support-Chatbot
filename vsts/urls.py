from django.conf.urls import url
from .views import receiveWebhook
#url for app

app_name = 'vsts'

urlpatterns = [
    url(r'^$', receiveWebhook, name='vsts'),
]