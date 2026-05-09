from datetime import date

from django.utils.translation import get_language

from .models import CompanySetting


def company_settings(request):
    return {
        'company_settings': CompanySetting.get_settings(),
    }


def current_language(request):
    return {
        'current_language': get_language(),
    }


def today_date(request):
    return {
        'today': date.today(),
    }


def unread_notifications(request):
    count = 0
    if request.user.is_authenticated:
        from .models import Notification
        count = Notification.objects.filter(recipient=request.user, read=False).count()
    return {
        'unread_notifications': count,
    }


from django.core.cache import cache


def system_labels(request):
    labels = cache.get('system_labels_all')
    if labels is None:
        from .models import SystemLabel
        qs = SystemLabel.objects.filter(is_active=True).exclude(value_ar='')
        labels = {obj.key: obj.value_ar for obj in qs}
        cache.set('system_labels_all', labels, 300)
    return {'system_labels': labels}
