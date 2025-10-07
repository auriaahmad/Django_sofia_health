from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import AppointmentForm
from .models import Appointment


def create_appointment(request):
    """View for creating a new appointment."""

    if request.method == 'POST':
        form = AppointmentForm(request.POST)

        if form.is_valid():
            # Save appointment to database
            appointment = form.save()
            # Store appointment ID in session for payment flow
            request.session['pending_appointment_id'] = appointment.id
            # Redirect to payment page
            return redirect('payment_create')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AppointmentForm()

    context = {
        'form': form,
        'title': 'Book Appointment'
    }

    return render(request, 'appointments/create.html', context)


def appointment_list(request):
    """View for listing all appointments."""

    appointments = Appointment.objects.all().order_by('-appointment_time')
    paid_count = appointments.filter(is_paid=True).count()
    pending_count = appointments.filter(is_paid=False).count()

    context = {
        'appointments': appointments,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'title': 'Appointments'
    }

    return render(request, 'appointments/list.html', context)


def appointment_success(request):
    """View shown after successful appointment booking and payment."""

    appointment_id = request.session.get('completed_appointment_id')

    if appointment_id:
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            # Clear session
            del request.session['completed_appointment_id']

            context = {
                'appointment': appointment,
                'title': 'Booking Confirmed'
            }

            return render(request, 'appointments/success.html', context)
        except Appointment.DoesNotExist:
            pass

    messages.warning(request, 'No appointment found.')
    return redirect('create_appointment')
