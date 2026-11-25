from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, UpdateView, CreateView, View
from django.urls import reverse_lazy
from django.db.models import Sum, Q, F
from products.models import Product
from orders.models import Order, OrderItem
from users.models import Vendor
from users.forms import ProductForm


@login_required
def vendor_dashboard(request):
    """Панель продавца — общая статистика."""
    vendor, created = Vendor.objects.get_or_create(owner=request.user)
    if created:
        messages.info(request, 'Ваш магазин создан. Ожидайте модерации.')

    total_products = vendor.products.count()
    total_orders = OrderItem.objects.filter(vendor=vendor).values('order').distinct().count()
    total_revenue = OrderItem.objects.filter(vendor=vendor).aggregate(
        total=Sum(F('price') * F('quantity'))
    )['total'] or 0

    recent_orders = OrderItem.objects.filter(
        vendor=vendor
    ).select_related('order').order_by('-order__created_at')[:10]

    return render(request, 'vendors/dashboard.html', {
        'vendor': vendor,
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
    })


class ProductListView(ListView):
    """Список товаров продавца."""
    model = Product
    template_name = 'vendors/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        return vendor.products.select_related('category').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        context['vendor'] = vendor
        return context


class ProductCreateView(CreateView):
    """Создание товара."""
    model = Product
    form_class = ProductForm
    template_name = 'vendors/product_form.html'
    context_object_name = 'product'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        context['vendor'] = vendor
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        form.instance.vendor = vendor
        messages.success(self.request, 'Товар сохранён.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vendors:product_list')


class ProductUpdateView(UpdateView):
    """Редактирование товара."""
    model = Product
    form_class = ProductForm
    template_name = 'vendors/product_form.html'
    context_object_name = 'product'

    def dispatch(self, request, *args, **kwargs):
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        product = get_object_or_404(Product, pk=kwargs['pk'], vendor=vendor)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        context['vendor'] = vendor
        context['is_edit'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Товар обновлён.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vendors:product_list')


class ProductDeleteView(ListView):
    """Удаление товара (POST only)."""
    model = Product
    template_name = 'vendors/product_confirm_delete.html'
    context_object_name = 'products'

    def dispatch(self, request, *args, **kwargs):
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        self.product = get_object_or_404(Product, pk=kwargs['pk'], vendor=vendor)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        context['vendor'] = vendor
        return context

    def post(self, request, *args, **kwargs):
        product = self.product
        product.delete()
        messages.success(request, f'Товар "{product.name}" удалён.')
        return redirect('vendors:product_list')


class VendorOrderListView(ListView):
    """Заказы, содержащие товары продавца."""
    model = OrderItem
    template_name = 'vendors/order_list.html'
    context_object_name = 'order_items'
    paginate_by = 20

    def get_queryset(self):
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        return OrderItem.objects.filter(
            vendor=vendor
        ).select_related('order', 'product').order_by('-order__created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor, _ = Vendor.objects.get_or_create(owner=self.request.user)
        context['vendor'] = vendor
        return context


class VendorOrderUpdateView(View):
    """Изменение статуса заказа (для товаров продавца)."""

    def get(self, request, *args, **kwargs):
        vendor, _ = Vendor.objects.get_or_create(owner=request.user)
        order_item = get_object_or_404(
            OrderItem.objects.select_related('order'),
            pk=kwargs['pk'],
            vendor=vendor,
        )
        return render(request, 'vendors/order_update.html', {
            'order_item': order_item,
            'order': order_item.order,
            'vendor': vendor,
            'status_choices': Order.STATUS_CHOICES,
        })

    def post(self, request, *args, **kwargs):
        vendor, _ = Vendor.objects.get_or_create(owner=request.user)
        order_item = get_object_or_404(
            OrderItem.objects.select_related('order'),
            pk=kwargs['pk'],
            vendor=vendor,
        )
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order_item.order.status = status
            order_item.order.save()
            messages.success(request, 'Статус заказа обновлён.')
        return redirect('vendors:order_list')
