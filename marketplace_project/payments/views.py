from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.views.decorators.http import require_POST
from orders.models import Order


from decimal import Decimal

@login_required
def topup_balance(request):
    """Пополнение баланса."""
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if amount:
            try:
                amount = Decimal(amount)
                if amount > 0 and amount <= 100000:
                    with transaction.atomic():
                        request.user.balance += amount
                        request.user.save()
                    messages.success(request, f'Баланс пополнен на {amount:,.2f} ₽')
                    return redirect('payments:topup')
            except Exception:
                pass
        messages.error(request, 'Некорректная сумма')
        return redirect('payments:topup')

    return render(request, 'users/topup_balance.html')


@login_required
@require_POST
def pay_order(request, order_id):
    """Оплата заказа с баланса."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if order.status != 'new':
        messages.error(request, 'Этот заказ нельзя оплатить')
        return redirect('orders:order_detail', pk=order_id)

    if request.user.balance < order.total_price:
        messages.error(
            request,
            f'Недостаточно средств. На балансе: {request.user.balance:,.2f} ₽, нужно: {order.total_price:,.2f} ₽'
        )
        return redirect('orders:order_detail', pk=order_id)

    with transaction.atomic():
        request.user.balance -= order.total_price
        request.user.save()
        order.status = 'processing'
        order.save()

    messages.success(request, f'Заказ #{order.id} оплачен!')
    return redirect('orders:order_detail', pk=order_id)


def payment_success(request):
    return render(request, 'payments/success.html')


def payment_cancel(request):
    return render(request, 'payments/cancel.html')
