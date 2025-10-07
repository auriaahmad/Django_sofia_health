from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Admin configuration for Appointment model."""

    list_display = [
        'provider_name',
        'client_email',
        'appointment_time',
        'is_paid',
        'created_at'
    ]

    list_filter = [
        'is_paid',
        'appointment_time',
        'created_at'
    ]

    search_fields = [
        'provider_name',
        'client_email',
        'payment_intent_id'
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'payment_intent_id'
    ]

    fieldsets = (
        ('Appointment Details', {
            'fields': ('provider_name', 'client_email', 'appointment_time')
        }),
        ('Payment Information', {
            'fields': ('is_paid', 'payment_intent_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    ordering = ['-appointment_time']
