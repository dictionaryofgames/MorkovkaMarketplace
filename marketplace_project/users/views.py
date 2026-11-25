from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView
from .forms import UserRegistrationForm, UserLoginForm, VendorCreateForm
from .models import CustomUser, Vendor


def register(request):
    """Регистрация нового пользователя."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            if user.role == 'seller':
                vendor, created = Vendor.objects.get_or_create(owner=user)
                if created:
                    messages.info(request, 'Магазин создан. Ожидайте модерации.')
                return redirect('vendors:dashboard')
            return redirect('store:home')
        messages.error(request, 'Пожалуйста, исправьте ошибки ниже.')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """Вход в систему."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.get_username()}!')
            return redirect('store:home')
        messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    """Выход из системы."""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('store:home')


@login_required
def profile(request, pk):
    """Личный кабинет пользователя."""
    user = get_object_or_404(CustomUser, pk=pk)
    is_own_profile = request.user == user

    vendor = None
    if user.is_seller:
        vendor, _ = Vendor.objects.get_or_create(owner=user)

    if request.method == 'POST' and is_own_profile:
        if 'vendor_name' in request.POST and vendor:
            new_name = request.POST.get('vendor_name', '').strip()
            if new_name:
                vendor.name = new_name
                if not vendor.slug:
                    vendor.slug = f'shop-{vendor.id}'
                vendor.save()
                messages.success(request, 'Название магазина обновлено.')
            else:
                messages.error(request, 'Название магазина не может быть пустым.')
        return redirect('users:profile', pk=user.pk)

    return render(request, 'users/profile.html', {
        'user': user,
        'vendor': vendor,
        'is_own_profile': is_own_profile,
    })


class VendorDetailView(TemplateView):
    """Страница магазина продавца."""
    template_name = 'store/vendor_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vendor = get_object_or_404(Vendor, slug=kwargs['slug'])
        context['vendor'] = vendor
        context['products'] = vendor.products.filter(is_active=True)
        return context


@login_required
def create_vendor(request):
    """Создание магазина продавцом."""
    if not request.user.is_seller:
        messages.error(request, 'Только пользователи с ролью "Продавец" могут создавать магазины.')
        return redirect('store:home')

    vendor = Vendor.objects.filter(owner=request.user).first()
    if vendor:
        messages.info(request, 'У вас уже есть магазин.')
        return redirect('store:vendor_detail', slug=vendor.slug)

    if request.method == 'POST':
        form = VendorCreateForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.owner = request.user
            if not vendor.name:
                vendor.name = f'Магазин {request.user.get_username()}'
            vendor.save()
            messages.success(request, 'Магазин создан! Ожидайте модерации.')
            return redirect('store:vendor_detail', slug=vendor.slug)
    else:
        form = VendorCreateForm()

    return render(request, 'users/create_vendor.html', {'form': form})
