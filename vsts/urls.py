from django.conf.urls import url
from .views import notification, authorize
#url for app

app_name = 'vsts'

urlpatterns = [
    url(r'^$', notification, name='vsts'),
    url(r'^oauth/$', authorize, name='oauth'),
]