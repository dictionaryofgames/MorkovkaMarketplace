from django.conf import settings
from django.db import models
from django.utils import timezone


class Order(models.Model):
    """Заказ покупателя."""

    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name='Покупатель',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус',
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Общая сумма',
    )
    shipping_address = models.TextField(verbose_name='Адрес доставки')
    shipping_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон для связи',
    )
    comment = models.TextField(
        blank=True,
        default='',
        verbose_name='Комментарий к заказу',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} — {self.user.get_username()}'

    @property
    def is_paid(self):
        return self.status in ('shipped', 'delivered')


class OrderItem(models.Model):
    """Позиция заказа."""

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='items',
        verbose_name='Заказ',
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name='Товар',
    )
    vendor = models.ForeignKey(
        'users.Vendor',
        on_delete=models.PROTECT,
        verbose_name='Продавец',
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за единицу',
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product} x {self.quantity}'

    @property
    def total(self):
        return self.price * self.quantity
