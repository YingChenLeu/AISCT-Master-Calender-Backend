from django.urls import path
from . import views

urlpatterns = [
    path("", views.Index, name="index"),
    path("events/getrange/", views.getEventsRange, name="get_events"),
    path("events/add/", views.addEvent, name="add_event"),
]