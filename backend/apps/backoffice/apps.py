from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BackofficeConfig(AppConfig):
    name = 'apps.backoffice'
    verbose_name = _('التحكم في النظام')
