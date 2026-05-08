from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Account(models.Model):
    class Type(models.TextChoices):
        ASSET = 'asset', _('أصل')
        LIABILITY = 'liability', _('خصم')
        EQUITY = 'equity', _('حقوق ملكية')
        INCOME = 'income', _('إيراد')
        EXPENSE = 'expense', _('مصروف')

    code = models.CharField(_('كود الحساب'), max_length=20, unique=True)
    name = models.CharField(_('الاسم (إنجليزي)'), max_length=200)
    name_ar = models.CharField(_('الاسم (عربي)'), max_length=200)
    account_type = models.CharField(
        _('نوع الحساب'), max_length=20, choices=Type.choices
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children', verbose_name=_('حساب أب')
    )
    is_active = models.BooleanField(_('نشط'), default=True)
    opening_balance = models.DecimalField(
        _('رصيد افتتاحي'), max_digits=14, decimal_places=2, default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('حساب')
        verbose_name_plural = _('دليل الحسابات')
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.name_ar or self.name}'

    def balance(self):
        debits = JournalLine.objects.filter(account=self).aggregate(
            total=models.Sum('debit')
        )['total'] or 0
        credits = JournalLine.objects.filter(account=self).aggregate(
            total=models.Sum('credit')
        )['total'] or 0
        if self.account_type in ('asset', 'expense'):
            return self.opening_balance + debits - credits
        return self.opening_balance + credits - debits


class JournalEntry(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('مسودة')
        POSTED = 'posted', _('مرحل')
        CANCELLED = 'cancelled', _('ملغي')

    entry_number = models.CharField(
        _('رقم القيد'), max_length=30, unique=True, editable=False
    )
    entry_date = models.DateField(_('تاريخ القيد'))
    description = models.TextField(_('البيان'))
    reference_type = models.CharField(
        _('نوع المرجع'), max_length=50, null=True, blank=True
    )
    reference_id = models.IntegerField(
        _('رقم المرجع'), null=True, blank=True
    )
    status = models.CharField(
        _('الحالة'), max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name=_('تم بواسطة')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    posted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('قيد محاسبي')
        verbose_name_plural = _('القيود المحاسبية')
        ordering = ['-entry_date', '-id']

    def __str__(self):
        return f'{self.entry_number} - {self.entry_date}'

    def total_debit(self):
        return self.lines.aggregate(total=models.Sum('debit'))['total'] or 0

    def total_credit(self):
        return self.lines.aggregate(total=models.Sum('credit'))['total'] or 0

    def is_balanced(self):
        return self.total_debit() == self.total_credit()

    def save(self, *args, **kwargs):
        if not self.entry_number:
            year = self.entry_date.year
            prefix = f'JE-{year}-'
            last = JournalEntry.objects.filter(
                entry_number__startswith=prefix
            ).order_by('entry_number').last()
            if last:
                last_num = int(last.entry_number.split('-')[-1])
                self.entry_number = f'{prefix}{last_num + 1:04d}'
            else:
                self.entry_number = f'{prefix}0001'
        super().save(*args, **kwargs)


class JournalLine(models.Model):
    entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE,
        related_name='lines', verbose_name=_('القيد')
    )
    account = models.ForeignKey(
        Account, on_delete=models.PROTECT,
        related_name='journal_lines', verbose_name=_('الحساب')
    )
    debit = models.DecimalField(
        _('مدين'), max_digits=14, decimal_places=2, default=0
    )
    credit = models.DecimalField(
        _('دائن'), max_digits=14, decimal_places=2, default=0
    )
    description = models.CharField(
        _('البيان'), max_length=500, blank=True
    )

    class Meta:
        verbose_name = _('تفصيل قيد')
        verbose_name_plural = _('تفاصيل القيود')

    def __str__(self):
        return f'{self.account} - {self.debit or self.credit}'
