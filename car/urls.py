from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.index, name='car_index'),  # це для /
    path('car/<int:id>/', views.car_detail, name='car_detail'),
    path('car/gallery/<int:id>/', views.car_gallery, name='car_gallery'),
    path('car/', views.index, name='car_index_url'),   
     path('car/create/', views.create_car, name='car_create'),
    path('car/delete/<int:id>/', views.delete_car, name='car_delete'),
    path('edit/<int:id>/', views.edit_car, name='car_edit'),  
    path('catalog/', views.catalog, name='catalog'),
    path('rent/', views.rent_car, name='rent_car'),
    path('favorites/', views.favorites_list, name='favorites_list'),
    path('favorites/add/<int:car_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:car_id>/', views.remove_from_favorites, name='remove_from_favorites'),
]
