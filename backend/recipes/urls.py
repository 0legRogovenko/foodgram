from api.views import short_link_redirect
from django.urls import path

urlpatterns = [
    path('<str:code>/', short_link_redirect, name='short-link'),
]
