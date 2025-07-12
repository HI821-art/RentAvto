from django.shortcuts import render, redirect, get_object_or_404
from .models import Car, Booking
from .forms.create import CarForm
from .forms.edit import EditCarForm
from .forms.booking import BookingForm
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib import messages
def index(request):
    return render(request, "car_index.html")

def catalog(request):
    car_list = Car.objects.all().order_by("id")
    page_number = request.GET.get("page", 1)
    page_size = request.GET.get("size", 5)
    paginator = Paginator(car_list, page_size)
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "catalog.html",
        {
            "cars": page_obj.object_list,
            "count": paginator.count,
            "page_obj": page_obj,
            "page_size": page_size,
        },
    )

def car_detail(request, id):
    car = get_object_or_404(Car, id=id)
    return render(request, 'car_detail.html', {'car': car})

def car_gallery(request, id):
    car = get_object_or_404(Car, id=id)
    photos = []  
    return render(request, 'car_gallery.html', {'car': car, 'photos': photos})

def create_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('car_index')
    else:
        form = CarForm()
    return render(request, 'create.html', {'form': form})

def delete_car(request, id):
    if id <= 0:
        return HttpResponse("Invalid ID")
    car = get_object_or_404(Car, pk=id)
    if request.method == "POST":
        if hasattr(car, "image") and car.image:
            car.image.delete(save=False)
        car.delete()
        return redirect('car_index')
    return render(request, "delete.html", {"car": car})

def edit_car(request, id):
    car = get_object_or_404(Car, pk=id)
    form = EditCarForm(instance=car)
    if request.method == "POST":
        form = EditCarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            if request.FILES and hasattr(car, "image") and car.image:
                car.image.delete(save=False)
            form.save()
            return redirect('car_index')
    return render(request, "create.html", {"form": form, "edit": True, "car": car})

from .forms.booking import BookingForm

def rent_car(request):
    car_id = request.GET.get('car_id')
    initial = {}
    booked_ranges = []
    if car_id:
        initial['car'] = car_id
        booked_ranges = Booking.objects.filter(car=car_id).values('date_from', 'date_to')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            car = form.cleaned_data['car']
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']

            overlap = Booking.objects.filter(
                car=car,
                date_from__lte=date_to,
                date_to__gte=date_from
            ).exists()
            if overlap:
                messages.error(request, "Цей автомобіль вже заброньований на вибрані дати.")
            else:
                form.save()
                return render(request, './rent_success.html')
    else:
        form = BookingForm(initial=initial)
    return render(request, './rent_car.html', {'form': form, 'booked_ranges': booked_ranges})