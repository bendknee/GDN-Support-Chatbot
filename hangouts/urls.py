from django.conf.urls import url
from .views import receive_message
#url for app

app_name = 'hangouts'

urlpatterns = [
    url(r'^$', receive_message, name='hangouts'),
]