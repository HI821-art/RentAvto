from django.contrib import admin
from .models import Car, Booking

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('id', 'brand', 'model', 'year', 'available')
    list_filter = ('brand', 'year', 'available')
    search_fields = ('brand', 'model')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'user', 'date_from', 'date_to', 'status')
    list_filter = ('status', 'date_from', 'date_to')
    search_fields = ('car__brand', 'car__model', 'user__username')