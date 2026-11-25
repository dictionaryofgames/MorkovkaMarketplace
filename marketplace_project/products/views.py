from django.db.models import Q, Avg
from django.shortcuts import render, get_object_or_404
from products.models import Category, Product
from users.models import Vendor


def home(request):
    """Главная страница — категории и последние товары."""
    categories = Category.objects.filter(is_active=True).prefetch_related('products')
    latest_products = Product.objects.select_related('vendor', 'category').filter(
        is_active=True
    ).order_by('-created_at')[:12]

    featured_products = Product.objects.select_related('vendor', 'category').filter(
        is_active=True
    ).order_by('-created_at')[:4]

    return render(request, 'store/home.html', {
        'categories': categories,
        'latest_products': latest_products,
        'featured_products': featured_products,
    })


def category_detail(request, slug):
    """Страница категории с фильтрацией."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.select_related('vendor', 'category').filter(
        category=category,
        is_active=True,
    )

    # Фильтр по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Фильтр по продавцу
    vendor_id = request.GET.get('vendor')
    if vendor_id:
        products = products.filter(vendor_id=vendor_id)

    # Все продавцы для фильтра
    vendors = Vendor.objects.filter(
        products__category=category,
        status='active',
    ).distinct()

    return render(request, 'store/category_detail.html', {
        'category': category,
        'products': products,
        'vendors': vendors,
        'min_price': min_price,
        'max_price': max_price,
    })


def product_detail(request, slug):
    """Страница товара."""
    product = get_object_or_404(
        Product.objects.select_related('vendor', 'category').prefetch_related(
            'order_items'
        ),
        slug=slug,
        is_active=True,
    )

    # Похожие товары
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
    ).exclude(pk=product.pk)[:4]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


def search(request):
    """Поиск товаров."""
    query = request.GET.get('q', '').strip()
    products = Product.objects.select_related('vendor', 'category').filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True,
    ).distinct()

    return render(request, 'store/search.html', {
        'query': query,
        'products': products,
    })


def vendor_detail(request, slug):
    """Страница магазина."""
    vendor = get_object_or_404(Vendor, slug=slug)
    products = Product.objects.select_related('vendor', 'category').filter(
        vendor=vendor,
        is_active=True,
    )

    return render(request, 'store/vendor_detail.html', {
        'vendor': vendor,
        'products': products,
    })
