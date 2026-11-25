from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart, CartItem


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

    # Привязываем сессионную корзину к пользователю при логине
    if request.user.is_authenticated and cart.session_key and not cart.user:
        cart.user = request.user
        cart.save()

    return cart


def cart_summary(request):
    """Страница корзины."""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product__vendor').all()

    return render(request, 'cart/cart_summary.html', {
        'cart': cart,
        'cart_items': cart_items,
    })


@require_POST
def cart_add(request, product_id):
    """Добавление товара в корзину."""
    product = get_object_or_404(Product, pk=product_id)

    if not product.is_in_stock:
        messages.error(request, 'Товара нет в наличии.')
        return redirect('store:product_detail', slug=product.slug)

    cart = get_or_create_cart(request)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    if not created:
        cart_item.quantity += 1
        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
            messages.warning(request, 'Превышено количество на складе.')

    cart_item.save()
    messages.success(request, f'{product.name} добавлен в корзину.')
    return redirect('cart:summary')


@require_POST
def cart_update(request, item_id):
    """Обновление количества товара в корзине."""
    cart_item = get_object_or_404(CartItem, pk=item_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Позиция удалена из корзины.')
    else:
        if quantity > cart_item.product.stock:
            quantity = cart_item.product.stock
            messages.warning(request, 'Превышено количество на складе.')
        cart_item.quantity = quantity
        cart_item.save()

    return redirect('cart:summary')


@require_POST
def cart_remove(request, item_id):
    """Удаление товара из корзины."""
    cart_item = get_object_or_404(CartItem, pk=item_id)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.info(request, f'{product_name} удалён из корзины.')
    return redirect('cart:summary')
