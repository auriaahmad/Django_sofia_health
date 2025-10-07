from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Appointment
from .forms import AppointmentForm


class AppointmentModelTest(TestCase):
    """Test cases for Appointment model."""

    def setUp(self):
        """Set up test data."""
        self.future_time = timezone.now() + timedelta(days=1)

        self.appointment = Appointment.objects.create(
            provider_name="Dr. Smith",
            client_email="client@example.com",
            appointment_time=self.future_time
        )

    def test_appointment_creation(self):
        """Test appointment is created correctly."""
        self.assertEqual(self.appointment.provider_name, "Dr. Smith")
        self.assertEqual(self.appointment.client_email, "client@example.com")
        self.assertFalse(self.appointment.is_paid)
        self.assertIsNone(self.appointment.payment_intent_id)

    def test_appointment_str(self):
        """Test string representation of appointment."""
        expected = f"Dr. Smith - client@example.com at {self.future_time}"
        self.assertEqual(str(self.appointment), expected)

    def test_is_upcoming(self):
        """Test is_upcoming method."""
        self.assertTrue(self.appointment.is_upcoming())

        # Create past appointment
        past_appointment = Appointment.objects.create(
            provider_name="Dr. Jones",
            client_email="past@example.com",
            appointment_time=timezone.now() - timedelta(days=1)
        )
        self.assertFalse(past_appointment.is_upcoming())


class AppointmentFormTest(TestCase):
    """Test cases for AppointmentForm."""

    def test_valid_form(self):
        """Test form with valid data."""
        future_time = timezone.now() + timedelta(days=1)
        data = {
            'provider_name': 'Dr. Smith',
            'client_email': 'test@example.com',
            'appointment_time': future_time
        }
        form = AppointmentForm(data=data)
        self.assertTrue(form.is_valid())

    def test_past_appointment_invalid(self):
        """Test form rejects past appointment times."""
        past_time = timezone.now() - timedelta(hours=1)
        data = {
            'provider_name': 'Dr. Smith',
            'client_email': 'test@example.com',
            'appointment_time': past_time
        }
        form = AppointmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('appointment_time', form.errors)

    def test_invalid_email(self):
        """Test form rejects invalid email."""
        future_time = timezone.now() + timedelta(days=1)
        data = {
            'provider_name': 'Dr. Smith',
            'client_email': 'invalid-email',
            'appointment_time': future_time
        }
        form = AppointmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('client_email', form.errors)


class AppointmentViewTest(TestCase):
    """Test cases for Appointment views."""

    def test_create_appointment_get(self):
        """Test GET request to create appointment view."""
        response = self.client.get('/appointments/create/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')

    def test_appointment_list_get(self):
        """Test GET request to appointment list view."""
        response = self.client.get('/appointments/list/')
        self.assertEqual(response.status_code, 200)
