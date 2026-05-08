from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('مدير النظام')
        MANAGER = 'manager', _('مدير')
        SUPERVISOR = 'supervisor', _('مشرف')
        CASHIER = 'cashier', _('كاشير')
        STAFF = 'staff', _('موظف')
        CLIENT = 'client', _('عميل')

    class Language(models.TextChoices):
        ARABIC = 'ar', _('العربية')
        ENGLISH = 'en', _('English')

    phone = models.CharField(_('رقم الهاتف'), max_length=20, blank=True)
    client_discount_percent = models.DecimalField(_('نسبة خصم العميل'), max_digits=5, decimal_places=2, default=0)
    employee_id = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_('الموظف')
    )
    role = models.CharField(
        _('الدور'), max_length=20, choices=Role.choices,
        default=Role.STAFF
    )
    language_preference = models.CharField(
        _('اللغة'), max_length=2, choices=Language.choices,
        default=Language.ARABIC
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        verbose_name = _('مستخدم')
        verbose_name_plural = _('المستخدمين')
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name() or self.username}'
