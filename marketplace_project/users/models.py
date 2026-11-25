from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с ролями."""

    ROLE_CHOICES = (
        ('buyer', 'Покупатель'),
        ('seller', 'Продавец'),
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='buyer',
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар',
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Баланс',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_username() or self.email

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'pk': self.pk})

    @property
    def is_buyer(self):
        return self.role == 'buyer'

    @property
    def is_seller(self):
        return self.role == 'seller'


class UserProfile(models.Model):
    """Дополнительная информация о пользователе."""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    bio = models.TextField(blank=True, verbose_name='О себе')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user}'


class Vendor(models.Model):
    """Магазин / продавец на маркетплейсе."""

    STATUS_CHOICES = (
        ('pending', 'На модерации'),
        ('active', 'Активен'),
        ('rejected', 'Отклонено'),
        ('suspended', 'Приостановлен'),
    )

    owner = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='vendor',
        limit_choices_to={'role': 'seller'},
    )
    name = models.CharField(max_length=200, verbose_name='Название магазина')
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True, verbose_name='Описание')
    logo = models.ImageField(upload_to='vendors/', blank=True, null=True)
    email = models.EmailField(blank=True, verbose_name='Контактный email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    address = models.TextField(blank=True, verbose_name='Адрес магазина')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        verbose_name='Рейтинг',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if not self.slug:
                self.slug = slugify(self.name.lower()) or f'shop-{self.pk or id(self)}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:vendor_detail', kwargs={'slug': self.slug})
