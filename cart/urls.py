from django.urls import path

from cart import views

urlpatterns = [
    path("", views.index),
    path("clear/", views.clear),
    path("add/<int:id>", views.add),
    path("add/<int:id>/<int:quantity>", views.add),
]