from django import template

register = template.Library()

STATUS_CLASSES = {
    # Vendor status
    'pending': 'warning',
    'active': 'success',
    'rejected': 'danger',
    'suspended': 'secondary',
    # Order status
    'new': 'warning',
    'processing': 'info',
    'shipped': 'primary',
    'delivered': 'success',
    'cancelled': 'danger',
}


@register.filter
def status_class(value):
    """Возвращает Bootstrap CSS класс для статуса."""
    return STATUS_CLASSES.get(str(value), 'secondary')
