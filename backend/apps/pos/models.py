from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

SESSION_STATUS_CHOICES = [
    ('open', 'مفتوحة'),
    ('closed', 'مغلقة'),
]

PAYMENT_METHOD_CHOICES = [
    ('cash', 'نقدي'),
    ('card', 'بطاقة'),
    ('bank_transfer', 'تحويل بنكي'),
    ('multiple', 'متعدد'),
]

SALE_STATUS_CHOICES = [
    ('completed', 'مكتملة'),
    ('refunded', 'مسترجعة'),
    ('voided', 'ملغاة'),
]

ITEM_TYPE_CHOICES = [
    ('product', 'منتج'),
    ('service', 'خدمة'),
    ('material', 'خامة'),
]


class POSSession(models.Model):
    session_number = models.CharField(
        max_length=30, unique=True, verbose_name='رقم الجلسة'
    )
    cashier = models.ForeignKey(
        'employees.Employee', on_delete=models.PROTECT,
        verbose_name='الكاشير'
    )
    opened_at = models.DateTimeField(
        auto_now_add=True, verbose_name='وقت الفتح'
    )
    closed_at = models.DateTimeField(
        null=True, blank=True, verbose_name='وقت الإغلاق'
    )
    opening_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name='الرصيد الافتتاحي'
    )
    closing_balance = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='رصيد الإغلاق'
    )
    expected_balance = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='الرصيد المتوقع'
    )
    difference = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='الفارق'
    )
    status = models.CharField(
        max_length=10, choices=SESSION_STATUS_CHOICES,
        default='open', verbose_name='الحالة'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')

    class Meta:
        ordering = ['-opened_at']
        verbose_name = 'جلسة نقاط بيع'
        verbose_name_plural = 'جلسات نقاط البيع'

    def __str__(self):
        return f'{self.session_number} - {self.cashier}'

    def save(self, *args, **kwargs):
        if not self.session_number:
            from django.utils.timezone import localdate
            today = localdate()
            date_str = today.strftime('%Y%m%d')
            prefix = f'POS-{date_str}-'
            last = POSSession.objects.filter(
                session_number__startswith=prefix
            ).order_by('session_number').last()
            if last:
                try:
                    last_num = int(last.session_number.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            self.session_number = f'{prefix}{new_num:03d}'
        super().save(*args, **kwargs)


class POSSale(models.Model):
    sale_number = models.CharField(
        max_length=30, unique=True, verbose_name='رقم الفاتورة'
    )
    session = models.ForeignKey(
        POSSession, on_delete=models.CASCADE,
        related_name='sales', verbose_name='الجلسة'
    )
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='العميل'
    )
    sale_date = models.DateTimeField(
        auto_now_add=True, verbose_name='تاريخ البيع'
    )
    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='المجموع الفرعي'
    )
    discount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name='الخصم'
    )
    tax = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name='الضريبة'
    )
    total = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='الإجمالي'
    )
    paid_amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='المبلغ المدفوع'
    )
    change_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name='الباقي'
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES,
        verbose_name='طريقة الدفع'
    )
    status = models.CharField(
        max_length=20, choices=SALE_STATUS_CHOICES,
        default='completed', verbose_name='الحالة'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        verbose_name='تم بواسطة'
    )

    class Meta:
        ordering = ['-sale_date']
        verbose_name = 'فاتورة بيع'
        verbose_name_plural = 'فواتير البيع'

    def __str__(self):
        return f'{self.sale_number} - {self.total}'

    def save(self, *args, **kwargs):
        if not self.sale_number:
            from django.utils.timezone import localdate
            today = localdate()
            date_str = today.strftime('%Y%m%d')
            prefix = f'PS-{date_str}-'
            last = POSSale.objects.filter(
                sale_number__startswith=prefix
            ).order_by('sale_number').last()
            if last:
                try:
                    last_num = int(last.sale_number.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            self.sale_number = f'{prefix}{new_num:04d}'
        super().save(*args, **kwargs)


class POSSaleItem(models.Model):
    sale = models.ForeignKey(
        POSSale, on_delete=models.CASCADE,
        related_name='items', verbose_name='الفاتورة'
    )
    item_type = models.CharField(
        max_length=20, choices=ITEM_TYPE_CHOICES, verbose_name='النوع'
    )
    description = models.CharField(
        max_length=255, verbose_name='الوصف'
    )
    material = models.ForeignKey(
        'inventory.Material', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='الخامة'
    )
    quantity = models.IntegerField(verbose_name='الكمية')
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='سعر الوحدة'
    )
    total = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name='الإجمالي'
    )

    class Meta:
        verbose_name = 'عنصر فاتورة'
        verbose_name_plural = 'عناصر الفاتورة'

    def __str__(self):
        return f'{self.description} x{self.quantity}'
