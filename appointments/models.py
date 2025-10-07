from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone


class Appointment(models.Model):
    """
    Appointment model for booking appointments with providers.

    Fields:
        provider_name: Name of the healthcare provider
        appointment_time: Scheduled date and time for the appointment
        client_email: Email address of the client booking the appointment
        created_at: Timestamp when the appointment was created
        updated_at: Timestamp when the appointment was last updated
        is_paid: Boolean indicating if payment has been completed
        payment_intent_id: Stripe PaymentIntent ID for tracking payments
    """

    provider_name = models.CharField(
        max_length=255,
        help_text="Name of the healthcare provider"
    )

    appointment_time = models.DateTimeField(
        help_text="Scheduled date and time for the appointment"
    )

    client_email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Email address of the client"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when appointment was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when appointment was last updated"
    )

    is_paid = models.BooleanField(
        default=False,
        help_text="Payment status of the appointment"
    )

    payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Stripe PaymentIntent ID"
    )

    class Meta:
        ordering = ['-appointment_time']
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

    def __str__(self):
        return f"{self.provider_name} - {self.client_email} at {self.appointment_time}"

    def is_upcoming(self):
        """Check if the appointment is in the future."""
        return self.appointment_time > timezone.now()
