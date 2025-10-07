"""
Stripe payment service module.

This module handles all Stripe-related payment operations,
keeping the business logic separate from views.
"""

import stripe
from django.conf import settings
from typing import Dict, Optional


# Configure Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service class for handling Stripe payment operations."""

    @staticmethod
    def create_payment_intent(
        amount: int,
        currency: str = 'usd',
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a Stripe PaymentIntent.

        Args:
            amount: Payment amount in cents (e.g., 5000 for $50.00)
            currency: Currency code (default: 'usd')
            metadata: Optional metadata to attach to the payment

        Returns:
            Dict containing PaymentIntent details including client_secret

        Raises:
            stripe.error.StripeError: If payment intent creation fails
        """
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                }
            )

            return {
                'id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'status': payment_intent.status,
            }

        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> Dict:
        """
        Retrieve a PaymentIntent by ID.

        Args:
            payment_intent_id: The Stripe PaymentIntent ID

        Returns:
            Dict containing PaymentIntent details

        Raises:
            stripe.error.StripeError: If retrieval fails
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            return {
                'id': payment_intent.id,
                'amount': payment_intent.amount,
                'currency': payment_intent.currency,
                'status': payment_intent.status,
                'metadata': payment_intent.metadata,
            }

        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def confirm_payment(payment_intent_id: str) -> bool:
        """
        Check if a payment has been successfully completed.

        Args:
            payment_intent_id: The Stripe PaymentIntent ID

        Returns:
            Boolean indicating if payment succeeded
        """
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent.status == 'succeeded'

        except stripe.error.StripeError:
            return False


def get_stripe_publishable_key() -> str:
    """
    Get the Stripe publishable key from settings.

    Returns:
        Stripe publishable key for client-side use
    """
    return settings.STRIPE_PUBLIC_KEY
