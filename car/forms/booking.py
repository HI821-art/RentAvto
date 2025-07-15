from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from ..models import Booking, Car

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['car', 'name', 'email', 'phone', 'date_from', 'date_to']
        widgets = {
            'date_from': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().strftime('%Y-%m-%d')
            }),
            'date_to': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введіть ваше повне ім\'я'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+380XXXXXXXXX'
            }),
            'car': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'car': 'Автомобіль',
            'name': 'Повне ім\'я',
            'email': 'Email',
            'phone': 'Номер телефону',
            'date_from': 'Дата початку оренди',
            'date_to': 'Дата закінчення оренди'
        }
        help_texts = {
            'phone': 'Введіть номер телефону у форматі +380XXXXXXXXX',
            'date_from': 'Дата не може бути раніше сьогоднішнього дня',
            'date_to': 'Дата повернення авто'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['car'].queryset = Car.objects.filter(available=True)
        self.fields['car'].label_from_instance = lambda obj: f"{obj.brand} {obj.model} ({obj.price_per_day} USD/день)"
        for field_name in self.fields:
            self.fields[field_name].required = True

    def clean_date_from(self):
        date_from = self.cleaned_data.get('date_from')
        if date_from and date_from < date.today():
            raise ValidationError("Дата початку оренди не може бути в минулому.")
        return date_from

    def clean_date_to(self):
        date_to = self.cleaned_data.get('date_to')
        if date_to and date_to <= date.today():
            raise ValidationError("Дата закінчення оренди повинна бути пізніше сьогоднішнього дня.")
        return date_to

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        car = cleaned_data.get('car')

        if date_from and date_to:
            duration = (date_to - date_from).days
            if date_from >= date_to:
                raise ValidationError("Дата закінчення повинна бути пізніше дати початку.")
            if duration > 365:
                raise ValidationError("Максимальний термін оренди — 365 днів.")
            if duration < 1:
                raise ValidationError("Мінімальний термін оренди — 1 день.")

        if car and date_from and date_to:
            overlapping = Booking.objects.filter(
                car=car,
                status__in=['pending', 'confirmed'],
                date_from__lt=date_to,
                date_to__gt=date_from
            )
            if self.instance and self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)
            if overlapping.exists():
                raise ValidationError(
                    f"Автомобіль {car.brand} {car.model} вже заброньований на ці дати. "
                    "Оберіть інший період або інше авто."
                )

        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            normalized = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not normalized.startswith('+'):
                normalized = '+' + normalized
            if len(normalized) < 10 or len(normalized) > 15:
                raise ValidationError("Введіть коректний номер телефону.")
            return normalized
        return phone