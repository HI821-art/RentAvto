from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from datetime import date
from .forms.create import CarForm
from .forms.edit import EditCarForm
from .forms.booking import BookingForm
from .models import Car, Booking


def index(request):
    cars = Car.objects.all()
    return render(request, "car_index.html", {'cars': cars})


from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q

def catalog(request):
    car_list = Car.objects.all().order_by("id")
    page_number = request.GET.get("page", 1)
    page_size = request.GET.get("size", 12)

    search_query = request.GET.get("search", "").strip()
    if search_query:
        car_list = car_list.filter(
            Q(brand__icontains=search_query) | Q(model__icontains=search_query)
        )

    paginator = Paginator(car_list, page_size)
    page_obj = paginator.get_page(page_number)

    return render(request, "catalog.html", {
        "cars": page_obj.object_list,
        "count": paginator.count,
        "page_obj": page_obj,
        "page_size": page_size,
    })

def car_detail(request, id):
    car = get_object_or_404(Car, id=id)
    is_booked = Booking.objects.filter(car=car, status__in=['pending', 'confirmed']).exists()
    return render(request, 'car_detail.html', {
        'car': car,
        'is_booked': is_booked,
    })


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
    car = get_object_or_404(Car, pk=id)
    if request.method == "POST":
        if car.image:
            car.image.delete(save=False)
        car.delete()
        return redirect('car_index')
    return render(request, "delete.html", {"car": car})

    car = get_object_or_404(Car, pk=id)
    if request.method == "POST":
        form = EditCarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, f'Автомобіль "{car.brand} {car.model}" успішно оновлено!')
            return redirect('car_index')
        else:
            messages.error(request, 'Помилка при збереженні. Перевірте введені дані.')
    else:
        form = EditCarForm(instance=car)
    return render(request, "create.html", {
        "form": form,
        "edit": True,
        "car": car
    })

def edit_car(request, id):
    car = get_object_or_404(Car, pk=id)
    if request.method == "POST":
        form = EditCarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            messages.success(request, f'Автомобіль "{car.brand} {car.model}" успішно оновлено!')
            return redirect('car_index')
        else:
            messages.error(request, 'Помилка при збереженні. Перевірте введені дані.')
    else:
        form = EditCarForm(instance=car)
    return render(request, "create.html", {
        "form": form,
        "edit": True,
        "car": car
    })


@receiver(pre_save, sender=Car)
def delete_old_image(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_car = Car.objects.get(pk=instance.pk)
            if old_car.image and old_car.image != instance.image:
                old_car.image.delete(save=False)
        except Car.DoesNotExist:
            pass


def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    today = date.today()
    is_booked_now = Booking.objects.filter(
        car=car,
        status__in=['pending', 'confirmed'],
        date_from__lte=today,
        date_to__gte=today
    ).exists()
    return render(request, 'car_detail.html', {
        'car': car,
        'is_booked_now': is_booked_now
    })

def rent_car(request):
    car_id = request.GET.get('car_id')
    selected_car = None
    booked_ranges = []

    if car_id:
        selected_car = get_object_or_404(Car, id=car_id)
        if not selected_car.available:
            messages.warning(request, f'Автомобіль {selected_car.brand} {selected_car.model} наразі недоступний для оренди.')
            return redirect('car_catalog')
        booked_ranges = list(Booking.objects.filter(
            car=selected_car,
            status__in=['pending', 'confirmed']
        ).values('date_from', 'date_to'))

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            car = form.cleaned_data['car']
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']

            if date_from >= date_to or date_from < date.today():
                messages.error(request, "Некоректний період оренди.")
                return render(request, 'booking/rent_car.html', {
                    'form': form,
                    'selected_car': selected_car,
                    'booked_ranges': booked_ranges
                })

            overlap = Booking.objects.filter(
                car=car,
                status__in=['pending', 'confirmed'],
                date_from__lt=date_to,
                date_to__gt=date_from
            ).exists()

            if overlap:
                messages.error(request, "Цей автомобіль вже заброньований на вибрані дати.")
                return render(request, 'booking/rent_car.html', {
                    'form': form,
                    'selected_car': selected_car,
                    'booked_ranges': booked_ranges
                })

            booking = form.save(commit=False)
            booking.status = 'pending'
            booking.user = request.user
            booking.save()
            booking.car.available = False
            booking.car.save()
            messages.success(request, f"Ваше бронювання #{booking.id} створено!")
            return redirect('booking_success', booking_id=booking.id)
        
        else:
            messages.error(request, "Помилка при заповненні форми.")
    else:
        initial = {}
        if selected_car:
            initial['car'] = selected_car.id
        if request.user.is_authenticated:
            full_name = f"{request.user.first_name} {request.user.last_name}".strip()
            email = request.user.email
            for field in ['name', 'customer_name', 'full_name']:
                if field in BookingForm().fields:
                    initial[field] = full_name
            for field in ['email', 'customer_email']:
                if field in BookingForm().fields:
                    initial[field] = email
            for field in ['phone', 'customer_phone', 'phone_number']:
                if field in BookingForm().fields and hasattr(request.user, field):
                    initial[field] = getattr(request.user, field)
        form = BookingForm(initial=initial)

    return render(request, 'booking/rent_car.html', {
        'form': form,
        'selected_car': selected_car,
        'booked_ranges': booked_ranges,
        'cars': Car.objects.filter(available=True)
    })






def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    total_days = (booking.date_to - booking.date_from).days
    total_price = booking.car.price_per_day * total_days
    return render(request, 'booking/rent_success.html', {
        'booking': booking,
        'total_days': total_days,
        'total_price': total_price
    })


def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not request.user.is_staff:
        messages.error(request, "Немає прав на підтвердження.")
        return redirect('car_index')
    if booking.status != 'pending':
        messages.warning(request, f"Бронювання #{booking.id} вже має статус '{booking.get_status_display()}'.")
        return redirect('booking_list')
    if request.method == 'POST':
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, f"Бронювання #{booking.id} підтверджено.")
        return redirect('booking_list')
    return render(request, 'booking/confirm_booking.html', {'booking': booking})


@login_required
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not (request.user.is_staff or booking.user == request.user):
        return JsonResponse({'success': False, 'message': 'Немає прав для скасування.'})
    if booking.status == 'canceled':
        return JsonResponse({'success': False, 'message': f'Бронювання #{booking.id} вже скасовано.'})
    booking.status = 'canceled'
    booking.save()
    booking.car.available = True
    booking.car.save()
    messages.success(request, f"Бронювання #{booking.id} скасовано!")
    return JsonResponse({'success': True, 'message': f'Бронювання #{booking.id} скасовано!'})



def booking_list(request):
    status_filter = request.GET.get('status', 'all')
    bookings = Booking.objects.all() if status_filter == 'all' else Booking.objects.filter(status=status_filter)
    bookings = bookings.order_by('-created_at')
    for booking in bookings:
        booking.total_days = (booking.date_to - booking.date_from).days
        booking.calculated_total_price = booking.car.price_per_day * booking.total_days
    return render(request, 'booking/booking_list.html', {
        'bookings': bookings,
        'status_filter': status_filter,
        'status_choices': Booking._meta.get_field('status').choices
    })


def get_booked_dates(request, car_id):
    if request.method == 'GET':
        booked_ranges = list(Booking.objects.filter(
            car_id=car_id,
            status__in=['pending', 'confirmed']
        ).values('date_from', 'date_to'))

        for booking in booked_ranges:
            booking['date_from'] = booking['date_from'].strftime('%Y-%m-%d')
            booking['date_to'] = booking['date_to'].strftime('%Y-%m-%d')

        return JsonResponse({'booked_ranges': booked_ranges})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def add_to_favorites(request, car_id):
    favorites = request.session.get('favorites', [])
    if car_id not in favorites:
        favorites.append(car_id)
        request.session['favorites'] = favorites
    return redirect('car_detail', car_id=car_id)


def remove_from_favorites(request, car_id):
    favorites = request.session.get('favorites', [])
    if car_id in favorites:
        favorites.remove(car_id)
        request.session['favorites'] = favorites
    return redirect('favorites_list')


def favorites_list(request):
    favorites = request.session.get('favorites', [])
    favorite_cars = Car.objects.filter(id__in=favorites)
    return render(request, 'favorites_list.html', {'favorites': favorite_cars})


def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_index(request):
    return render(request, 'admin_index.html')
