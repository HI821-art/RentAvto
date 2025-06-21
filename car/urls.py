from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='car_index'),  # це для /
    path('car/<int:id>/', views.car_detail, name='car_detail'),
    path('car/gallery/<int:id>/', views.car_gallery, name='car_gallery'),
    path('car/', views.index, name='car_index_url'),   

      
]