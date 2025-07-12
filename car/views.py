from django.shortcuts import render, redirect, get_object_or_404
from .forms.create import CarForm
from .forms.edit import EditCarForm
from .forms.booking import BookingForm
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Car, Booking

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
    photos = car.photo_set.all()
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
                booking = form.save(commit=False)
                booking.status = 'pending'  # Початковий статус
                booking.save()
                messages.success(request, "Ваше бронювання відправлено на підтвердження!")
                return redirect('booking_success', booking_id=booking.id)
    else:
        form = BookingForm(initial=initial)
    return render(request, 'rent_car.html', {'form': form, 'booked_ranges': booked_ranges})

def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'rent_success.html', {'booking': booking})

def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user.is_staff:  # Перевірка, що це адміністратор
        booking.status = 'confirmed'
        booking.car.available = False  # Оновлюємо доступність
        booking.save()
        booking.car.save()
        messages.success(request, f"Бронювання {booking.id} підтверджено!")
    return redirect('booking_list')

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user.is_staff or booking.email == request.user.email:  # Адмін або власник
        booking.status = 'canceled'
        booking.save()
        messages.success(request, f"Бронювання {booking.id} скасовано!")
    return redirect('booking_list')

def booking_list(request):
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, 'booking_list.html', {'bookings': bookings})

def add_to_favorites(request, car_id):
    favorites = request.session.get('favorites', [])
    if car_id not in favorites:
        favorites.append(car_id)
        request.session['favorites'] = favorites
    return redirect('car_detail', id=car_id)

def remove_from_favorites(request, car_id):
    favorites = request.session.get('favorites', [])
    if car_id in favorites:
        favorites.remove(car_id)
        request.session['favorites'] = favorites
    return redirect('favorites_list')

def favorites_list(request):
    favorites = request.session.get('favorites', [])
    cars = Car.objects.filter(id__in=favorites)
    return render(request, 'favorites_list.html', {'cars': cars})