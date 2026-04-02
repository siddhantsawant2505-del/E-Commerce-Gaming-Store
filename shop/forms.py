from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'rating', 'email', 'phone', 'desc']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 0, 'max': 5, 'step': 0.5}),  # Allow half-star ratings
        }