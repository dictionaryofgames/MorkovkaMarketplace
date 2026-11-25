from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.db import transaction
from products.models import Product
from cart.models import Cart, CartItem
from .models import Order, OrderItem


@login_required
def checkout(request):
    """Оформление заказа."""
    cart = get_or_create_cart(request)

    if cart.items.count() == 0:
        messages.error(request, 'Корзина пуста.')
        return redirect('store:home')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '').strip()
        shipping_phone = request.POST.get('shipping_phone', '').strip()
        comment = request.POST.get('comment', '').strip()

        if not shipping_address:
            messages.error(request, 'Укажите адрес доставки.')
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'shipping_address': shipping_address,
                'shipping_phone': shipping_phone,
                'comment': comment,
            })

        try:
            with transaction.atomic():
                # Создаём заказ
                order = Order.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    shipping_phone=shipping_phone,
                    comment=comment,
                )

                # Создаём позиции заказа
                total = Decimal('0')
                for cart_item in cart.items.all():
                    product = cart_item.product
                    if product.stock < cart_item.quantity:
                        raise ValueError(
                            f'Недостаточно {product.name} на складе '
                            f'(есть: {product.stock}, нужно: {cart_item.quantity})'
                        )

                    item_total = product.price * cart_item.quantity
                    total += item_total

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        vendor=product.vendor,
                        quantity=cart_item.quantity,
                        price=product.price,
                    )

                    # Списание со склада
                    product.stock -= cart_item.quantity
                    product.save(update_fields=['stock'])

                order.total_price = total
                order.save(update_fields=['total_price'])

                # Очистка корзины
                cart.items.all().delete()
                cart.is_active = False
                cart.save()

                messages.success(
                    request,
                    f'Заказ #{order.id} успешно оформлен!',
                )
                return redirect('orders:order_detail', pk=order.pk)

        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'orders/checkout.html', {
                'cart': cart,
                'shipping_address': shipping_address,
                'shipping_phone': shipping_phone,
                'comment': comment,
            })

    return render(request, 'orders/checkout.html', {
        'cart': cart,
    })


@login_required
def order_list(request):
    """Список заказов покупателя."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    """Детали заказа покупателя."""
    from users.models import Vendor
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related(
            'items__product',
            'items__vendor',
        ),
        pk=pk,
    )
    # Покупатель или продавец товара в заказе могут смотреть заказ
    if request.user != order.user and not Vendor.objects.filter(owner=request.user).exists():
        from django.http import Http404
        raise Http404("Заказ не найден")
    return render(request, 'orders/order_detail.html', {'order': order})


def get_or_create_cart(request):
    """Возвращает активную корзину для пользователя/сессии."""
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(
            user=request.user,
            is_active=True,
        ).first()

    if not cart:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(
            session_key=session_key,
            is_active=True,
        )

    if request.user.is_authenticated and cart.session_key and not cart.user:
        cart.user = request.user
        cart.save()

    return cart
