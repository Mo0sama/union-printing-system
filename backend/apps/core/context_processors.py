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
    return {
        'unread_notifications': 0,
    }
