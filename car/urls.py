from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='car_index'),
    path('catalog/', views.catalog, name='car_catalog'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('car/<int:id>/gallery/', views.car_gallery, name='car_gallery'),
    path('create/', views.create_car, name='create_car'),
    path('delete/<int:id>/', views.delete_car, name='delete_car'),
    path('edit/<int:id>/', views.edit_car, name='edit_car'),
    path('rent/', views.rent_car, name='rent_car'),
    path('booking/<int:booking_id>/success/', views.booking_success, name='booking_success'),
    path('booking/<int:booking_id>/confirm/', views.confirm_booking, name='confirm_booking'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('favorites/add/<int:car_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:car_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.favorites_list, name='favorites_list'),
]