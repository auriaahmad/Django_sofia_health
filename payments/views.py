from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from appointments.models import Appointment
from .services.stripe_service import StripeService, get_stripe_publishable_key


def create_payment(request):
    """
    View for creating a Stripe payment for an appointment.
    """
    # Get pending appointment from session
    appointment_id = request.session.get('pending_appointment_id')

    if not appointment_id:
        messages.error(request, 'No appointment found. Please create an appointment first.')
        return redirect('create_appointment')

    try:
        appointment = Appointment.objects.get(id=appointment_id)
    except Appointment.DoesNotExist:
        messages.error(request, 'Appointment not found.')
        return redirect('create_appointment')

    # Create PaymentIntent (amount in cents, e.g., $50.00 = 5000 cents)
    amount = 5000  # $50.00 appointment fee

    try:
        payment_data = StripeService.create_payment_intent(
            amount=amount,
            metadata={
                'appointment_id': appointment.id,
                'provider_name': appointment.provider_name,
                'client_email': appointment.client_email,
            }
        )

        # Update appointment with payment intent ID
        appointment.payment_intent_id = payment_data['id']
        appointment.save()

        context = {
            'client_secret': payment_data['client_secret'],
            'stripe_public_key': get_stripe_publishable_key(),
            'amount': amount / 100,  # Convert to dollars for display
            'appointment': appointment,
            'title': 'Payment'
        }

        return render(request, 'payments/create.html', context)

    except Exception as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('create_appointment')


@require_http_methods(["POST"])
def confirm_payment(request):
    """
    API endpoint to confirm payment and complete appointment booking.
    """
    payment_intent_id = request.POST.get('payment_intent_id')

    if not payment_intent_id:
        return JsonResponse({'error': 'No payment intent ID provided'}, status=400)

    try:
        # Verify payment succeeded
        if StripeService.confirm_payment(payment_intent_id):
            # Find and update appointment
            appointment = Appointment.objects.get(payment_intent_id=payment_intent_id)
            appointment.is_paid = True
            appointment.save()

            # Store in session for success page
            request.session['completed_appointment_id'] = appointment.id

            return JsonResponse({
                'success': True,
                'redirect_url': '/appointments/success/'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Payment not confirmed'
            }, status=400)

    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Appointment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
