from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('topup/', views.topup_balance, name='topup'),
    path('pay-order/<int:order_id>/', views.pay_order, name='pay_order'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
]
