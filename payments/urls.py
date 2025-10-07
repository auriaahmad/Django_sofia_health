from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_payment, name='payment_create'),
    path('confirm/', views.confirm_payment, name='payment_confirm'),
]
