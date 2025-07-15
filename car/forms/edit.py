from django import forms
from ..models import Car

class EditCarForm(forms.ModelForm):
    class Meta:
        model = Car  
        fields = "__all__"
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        
        if 'description' in self.fields:
            self.fields['description'].widget.attrs['class'] = 'form-control'
            self.fields['description'].required = False