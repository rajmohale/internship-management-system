from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'cover_letter', 'offer_letter']
        widgets = {
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'cover_letter': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'offer_letter': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }