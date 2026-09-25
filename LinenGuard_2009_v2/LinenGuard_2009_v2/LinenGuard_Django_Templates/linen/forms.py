from django import forms
from django.utils import timezone
from .models import LinenItem, Train, Coach, LinenAssignment, CollectionSession, PassengerPNR


class LinenRegistrationForm(forms.ModelForm):
    custom_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control font-monospace',
            'placeholder': 'Leave empty for auto-generation (e.g. BL-20561)'
        }),
        help_text="Optional: Leave blank to automatically generate standard railway code prefix."
    )

    class Meta:
        model = LinenItem
        fields = ['linen_type', 'current_location']
        widgets = {
            'linen_type': forms.Select(attrs={'class': 'form-select'}),
            'current_location': forms.TextInput(attrs={'class': 'form-control', 'value': 'Central Railway Laundry'}),
        }


class LinenAssignmentForm(forms.ModelForm):
    linen_code = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control font-monospace',
            'placeholder': 'Enter Linen ID or scan QR (e.g., BL-20561)'
        })
    )

    class Meta:
        model = LinenAssignment
        fields = ['train', 'coach', 'berth', 'passenger_reference', 'journey_date']
        widgets = {
            'train': forms.Select(attrs={'class': 'form-select', 'id': 'train-select'}),
            'coach': forms.Select(attrs={'class': 'form-select', 'id': 'coach-select'}),
            'berth': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 36'}),
            'passenger_reference': forms.TextInput(attrs={'class': 'form-control', 'value': 'PNR-1001'}),
            'journey_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['journey_date'].initial = timezone.now().date()


class PassengerPNRForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pnr_number'].required = False

    class Meta:
        model = PassengerPNR
        fields = [
            'pnr_number', 'passenger_name', 'passenger_age', 'passenger_gender',
            'passenger_phone', 'passenger_email', 'passenger_address', 'ticket_image'
        ]
        widgets = {
            'pnr_number': forms.TextInput(attrs={'class': 'form-control font-monospace text-uppercase'}),
            'passenger_name': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 120}),
            'passenger_gender': forms.Select(
                choices=[('', 'Select'), ('Female', 'Female'), ('Male', 'Male'), ('Other', 'Other')],
                attrs={'class': 'form-select'}
            ),
            'passenger_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'passenger_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ticket_image': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class StartCollectionForm(forms.ModelForm):
    class Meta:
        model = CollectionSession
        fields = ['train', 'coach', 'journey_date', 'expected_quantity']
        widgets = {
            'train': forms.Select(attrs={'class': 'form-select'}),
            'coach': forms.Select(attrs={'class': 'form-select'}),
            'journey_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_quantity': forms.NumberInput(attrs={'class': 'form-control', 'value': 100}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['journey_date'].initial = timezone.now().date()
