from django.contrib.auth.views import LoginView, LogoutView
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model, login, logout, update_session_auth_hash
from django.shortcuts import redirect, render
import os
from django.contrib.auth.decorators import login_required
from car.models import Car
from django.urls import reverse
from django.contrib import messages
import re


if not hasattr(settings, 'SECRET_KEY'):
    settings.SECRET_KEY = os.urandom(32).hex()

class CustomLoginView(LoginView):
    template_name = 'auth/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        token = serializer.dumps({'user_id': user.id})
        response.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict')
        return response

    def get_success_url(self):
        return reverse('profile')

class CustomLogoutView(LogoutView):
    next_page = '/login/'

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        response = super().dispatch(request, *args, **kwargs)
        response.delete_cookie('auth_token')
        response.delete_cookie('sessionid')
        return HttpResponseRedirect(self.next_page)

def register_view(request):
    User = get_user_model()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', '1')

        if not all([username, email, password, confirm_password]):
            messages.error(request, "Усі поля, крім імені, прізвища та телефону, є обов'язковими.")
            return render(request, 'auth/register.html')

        if password != confirm_password:
            messages.error(request, 'Паролі не збігаються.')
            return render(request, 'auth/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Користувач із таким іменем уже існує.')
            return render(request, 'auth/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Користувач із такою електронною поштою вже існує.')
            return render(request, 'auth/register.html')

        if phone and not re.match(r'^\+380\d{9}$', phone):
            messages.error(request, 'Номер телефону повинен бути у форматі +380XXXXXXXXX')
            return render(request, 'auth/register.html')

        
        if phone and hasattr(User, 'phone'):
            if User.objects.filter(phone=phone).exists():
                messages.error(request, 'Користувач із таким номером телефону вже існує.')
                return render(request, 'auth/register.html')

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        if hasattr(user, 'phone'):
            user.phone = phone

        user.set_password(password)

     
        if role == '0':  # Admin
            user.is_staff = True
            user.is_superuser = True
        

        user.save()

        login(request, user)
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        token = serializer.dumps({'user_id': user.id})
        response = HttpResponseRedirect(reverse('profile'))
        response.set_cookie('auth_token', token, httponly=True, secure=True, samesite='Strict')
        messages.success(request, 'Реєстрація успішна!')
        return response

    return render(request, 'auth/register.html')

@login_required
def profile_view(request):
    bookings = request.user.bookings.filter(status__in=['pending', 'confirmed'])
    favorite_car_ids = request.session.get('favorites', [])
    favorite_cars = Car.objects.filter(id__in=favorite_car_ids)
    return render(request, 'auth/profile.html', {
        'bookings': bookings,
        'favorite_cars': favorite_cars,
        'user': request.user
    })

@login_required
def edit_profile_view(request):
    User = get_user_model()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        print(f"POST data: {dict(request.POST)}")
        print(f"Received data: username={username}, email={email}, phone={phone}")

        if not username or not email:
            messages.error(request, 'Ім\'я користувача та електронна пошта є обов\'язковими.')
            return render(request, 'auth/updateprofile.html')

        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, 'Користувач із таким іменем уже існує.')
            return render(request, 'auth/updateprofile.html')

        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, 'Користувач із такою електронною поштою вже існує.')
            return render(request, 'auth/updateprofile.html')

        if phone and not re.match(r'^\+380\d{9}$', phone):
            messages.error(request, 'Номер телефону повинен бути у форматі +380XXXXXXXXX')
            return render(request, 'auth/updateprofile.html')

        if phone and hasattr(request.user, 'phone'):
            if User.objects.filter(phone=phone).exclude(id=request.user.id).exists():
                messages.error(request, 'Користувач із таким номером телефону вже існує.')
                return render(request, 'auth/updateprofile.html')

        password_changed = False
        wants_password_change = any([current_password, new_password, confirm_password])

        if wants_password_change:
            if not current_password:
                messages.error(request, 'Для зміни пароля введіть поточний пароль.')
                return render(request, 'auth/updateprofile.html')

            if not request.user.check_password(current_password):
                messages.error(request, 'Поточний пароль введено неправильно.')
                return render(request, 'auth/updateprofile.html')

            if not new_password:
                messages.error(request, 'Введіть новий пароль.')
                return render(request, 'auth/updateprofile.html')

            if new_password != confirm_password:
                messages.error(request, 'Новий пароль та підтвердження пароля не збігаються.')
                return render(request, 'auth/updateprofile.html')

            if len(new_password) < 8:
                messages.error(request, 'Пароль повинен містити щонайменше 8 символів.')
                return render(request, 'auth/updateprofile.html')

            password_changed = True

        try:
            user = request.user
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name

            if hasattr(user, 'phone'):
                user.phone = phone if phone else None

            if password_changed:
                user.set_password(new_password)
                update_session_auth_hash(request, user)

            user.save()
            messages.success(request, 'Профіль оновлено!' if not password_changed else 'Профіль та пароль оновлено!')
            return redirect('profile')

        except Exception as e:
            print(f"Error saving user: {e}")
            messages.error(request, 'Сталася помилка при оновленні профілю. Спробуйте ще раз.')
            return render(request, 'auth/updateprofile.html')

    return render(request, 'auth/updateprofile.html')