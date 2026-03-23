from django import forms
from .models import PermissionRequest

class OfferLetterForm(forms.ModelForm):
    class Meta:
        model = PermissionRequest
        fields = ['offer_letter']


class CompletionForm(forms.ModelForm):
    class Meta:
        model = PermissionRequest
        fields = ['completion_certificate', 'feedback']