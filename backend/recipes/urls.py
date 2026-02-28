from django.urls import path

from api.views import short_link_redirect

urlpatterns = [
    path('<str:code>/', short_link_redirect, name='short-link'),
]
