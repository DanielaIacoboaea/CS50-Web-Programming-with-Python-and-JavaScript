from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("search", views.search, name="search"),
    path("new", views.addNew, name="addNew"),
    path("edit", views.edit, name="edit"),
    path("save", views.saveEdit, name="saveEdit"),
    path("random", views.randomEntry, name="randomEntry")
]
