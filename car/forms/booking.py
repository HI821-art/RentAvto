from django import forms
from ..models import Booking, Car

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['car', 'name', 'email', 'phone', 'date_from', 'date_to']
        widgets = {
            'date_from': forms.DateInput(attrs={'type': 'date'}),
            'date_to': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        self.fields['car'].label_from_instance = lambda obj: f"{obj.brand} {obj.model}"