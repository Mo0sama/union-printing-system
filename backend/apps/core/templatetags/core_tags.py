from datetime import datetime

from django import template
from django.urls import resolve, Resolver404
from django.utils import formats

register = template.Library()


@register.simple_tag(takes_context=True)
def active_url(context, url_name):
    request = context.get('request')
    if not request:
        return ''
    try:
        match = resolve(request.path_info)
        if url_name.endswith(':'):
            prefix = url_name[:-1]
            if match.namespace and match.namespace.startswith(prefix):
                return 'active'
        elif match.url_name == url_name:
            return 'active'
        elif match.namespace and f'{match.namespace}:{match.url_name}' == url_name:
            return 'active'
    except Resolver404:
        pass
    return ''


@register.filter
def currency(value):
    try:
        return f'{float(value):,.2f}'
    except (ValueError, TypeError):
        return '0.00'


@register.filter
def translate_status(value):
    status_map = {
        'pending': 'قيد الانتظار',
        'in_progress': 'قيد التنفيذ',
        'completed': 'مكتمل',
        'delivered': 'تم التسليم',
        'cancelled': 'ملغي',
        'approved': 'معتمد',
        'rejected': 'مرفوض',
        'draft': 'مسودة',
        'confirmed': 'مؤكد',
        'shipped': 'تم الشحن',
        'paid': 'مدفوع',
        'unpaid': 'غير مدفوع',
        'partial': 'مدفوع جزئياً',
        'active': 'نشط',
        'inactive': 'غير نشط',
        'new': 'جديد',
        'production': 'قيد الإنتاج',
        'quality_check': 'فحص الجودة',
        'ready': 'جاهز',
    }
    return status_map.get(value, str(value))


@register.filter
def lookup(d, key):
    return d.get(key, [])


@register.filter
def get_item(d, key):
    return d.get(key)


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def date_format(value, arg=None):
    if not value:
        return ''
    if arg:
        return datetime.strftime(value, arg)
    return formats.date_format(value, 'DATE_FORMAT')
