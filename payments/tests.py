from django.test import TestCase
from unittest.mock import patch, MagicMock
from appointments.models import Appointment
from django.utils import timezone
from datetime import timedelta
from .services.stripe_service import StripeService


class StripeServiceTest(TestCase):
    """Test cases for StripeService."""

    @patch('stripe.PaymentIntent.create')
    def test_create_payment_intent(self, mock_create):
        """Test PaymentIntent creation."""
        # Mock Stripe response
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = 'pi_test_123'
        mock_payment_intent.client_secret = 'pi_test_123_secret'
        mock_payment_intent.amount = 5000
        mock_payment_intent.currency = 'usd'
        mock_payment_intent.status = 'requires_payment_method'
        mock_create.return_value = mock_payment_intent

        # Call service method
        result = StripeService.create_payment_intent(
            amount=5000,
            metadata={'test': 'data'}
        )

        # Assertions
        self.assertEqual(result['id'], 'pi_test_123')
        self.assertEqual(result['amount'], 5000)
        self.assertEqual(result['currency'], 'usd')
        mock_create.assert_called_once()

    @patch('stripe.PaymentIntent.retrieve')
    def test_retrieve_payment_intent(self, mock_retrieve):
        """Test PaymentIntent retrieval."""
        # Mock Stripe response
        mock_payment_intent = MagicMock()
        mock_payment_intent.id = 'pi_test_123'
        mock_payment_intent.amount = 5000
        mock_payment_intent.currency = 'usd'
        mock_payment_intent.status = 'succeeded'
        mock_payment_intent.metadata = {'test': 'data'}
        mock_retrieve.return_value = mock_payment_intent

        # Call service method
        result = StripeService.retrieve_payment_intent('pi_test_123')

        # Assertions
        self.assertEqual(result['id'], 'pi_test_123')
        self.assertEqual(result['status'], 'succeeded')
        mock_retrieve.assert_called_once_with('pi_test_123')

    @patch('stripe.PaymentIntent.retrieve')
    def test_confirm_payment_success(self, mock_retrieve):
        """Test payment confirmation when succeeded."""
        # Mock Stripe response
        mock_payment_intent = MagicMock()
        mock_payment_intent.status = 'succeeded'
        mock_retrieve.return_value = mock_payment_intent

        # Call service method
        result = StripeService.confirm_payment('pi_test_123')

        # Assertions
        self.assertTrue(result)

    @patch('stripe.PaymentIntent.retrieve')
    def test_confirm_payment_failed(self, mock_retrieve):
        """Test payment confirmation when not succeeded."""
        # Mock Stripe response
        mock_payment_intent = MagicMock()
        mock_payment_intent.status = 'requires_payment_method'
        mock_retrieve.return_value = mock_payment_intent

        # Call service method
        result = StripeService.confirm_payment('pi_test_123')

        # Assertions
        self.assertFalse(result)


class PaymentViewTest(TestCase):
    """Test cases for payment views."""

    def setUp(self):
        """Set up test data."""
        self.future_time = timezone.now() + timedelta(days=1)
        self.appointment = Appointment.objects.create(
            provider_name="Dr. Smith",
            client_email="test@example.com",
            appointment_time=self.future_time
        )

    def test_create_payment_no_session(self):
        """Test create payment without appointment in session."""
        response = self.client.get('/payments/create/')
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(response.url.endswith('create/'))

    @patch('payments.views.StripeService.create_payment_intent')
    def test_create_payment_with_appointment(self, mock_create):
        """Test create payment with valid appointment."""
        # Mock Stripe response
        mock_create.return_value = {
            'id': 'pi_test_123',
            'client_secret': 'pi_test_123_secret',
            'amount': 5000,
            'currency': 'usd',
            'status': 'requires_payment_method'
        }

        # Set session
        session = self.client.session
        session['pending_appointment_id'] = self.appointment.id
        session.save()

        # Make request
        response = self.client.get('/payments/create/')

        # Note: This will fail without template, but tests the logic
        self.assertEqual(response.status_code, 200)
        mock_create.assert_called_once()
