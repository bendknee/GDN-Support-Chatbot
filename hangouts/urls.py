from django.conf.urls import url
from .views import receiveMessage
#url for app

app_name = 'hangouts'

urlpatterns = [
    url(r'^$', receiveMessage, name='hangouts'),
]