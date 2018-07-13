from django.conf.urls import url
from .views import receive_webhook
#url for app

app_name = 'vsts'

urlpatterns = [
    url(r'^$', receive_webhook, name='vsts'),
]