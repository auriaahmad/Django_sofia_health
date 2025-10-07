from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_appointment, name='create_appointment'),
    path('list/', views.appointment_list, name='appointment_list'),
    path('success/', views.appointment_success, name='appointment_success'),
]
