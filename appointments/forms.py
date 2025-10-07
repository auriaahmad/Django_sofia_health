from django import forms
from .models import Appointment


# Time slot choices from 8 AM to 10 PM (1-hour intervals)
TIME_SLOT_CHOICES = [
    ('08:00', '8:00 AM'),
    ('09:00', '9:00 AM'),
    ('10:00', '10:00 AM'),
    ('11:00', '11:00 AM'),
    ('12:00', '12:00 PM'),
    ('13:00', '1:00 PM'),
    ('14:00', '2:00 PM'),
    ('15:00', '3:00 PM'),
    ('16:00', '4:00 PM'),
    ('17:00', '5:00 PM'),
    ('18:00', '6:00 PM'),
    ('19:00', '7:00 PM'),
    ('20:00', '8:00 PM'),
    ('21:00', '9:00 PM'),
    ('22:00', '10:00 PM'),
]


class AppointmentForm(forms.ModelForm):
    """Form for creating appointments."""

    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Appointment Date'
    )

    appointment_time_slot = forms.ChoiceField(
        choices=TIME_SLOT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Time Slot'
    )

    class Meta:
        model = Appointment
        fields = ['provider_name', 'client_email']
        widgets = {
            'provider_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter provider name'
            }),
            'client_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
        }
        labels = {
            'provider_name': 'Provider Name',
            'client_email': 'Your Email',
        }

    def clean(self):
        """Validate appointment date and time."""
        from django.utils import timezone
        from datetime import datetime, time

        cleaned_data = super().clean()
        appointment_date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('appointment_time_slot')

        if appointment_date and time_slot:
            # Parse time slot (format: "HH:MM")
            hour, minute = map(int, time_slot.split(':'))
            appointment_datetime = datetime.combine(
                appointment_date,
                time(hour, minute)
            )

            # Make timezone aware
            appointment_datetime = timezone.make_aware(appointment_datetime)

            # Validate future datetime
            if appointment_datetime <= timezone.now():
                raise forms.ValidationError(
                    "Appointment must be in the future."
                )

            # Store combined datetime
            cleaned_data['appointment_time'] = appointment_datetime

        return cleaned_data

    def save(self, commit=True):
        """Save appointment with combined date and time."""
        instance = super().save(commit=False)
        instance.appointment_time = self.cleaned_data['appointment_time']

        if commit:
            instance.save()

        return instance
