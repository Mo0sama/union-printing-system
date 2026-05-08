from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.customers.models import Customer
from apps.quotes.models import Quote


class Order(models.Model):
    class OrderType(models.TextChoices):
        NORMAL = 'normal', _('عادي')
        URGENT = 'urgent', _('مستعجل')
        POS = 'pos', _('نقطة بيع')

    class Status(models.TextChoices):
        PENDING = 'pending', _('قيد الانتظار')
        CONFIRMED = 'confirmed', _('مؤكد')
        IN_DESIGN = 'in_design', _('في التصميم')
        IN_PRODUCTION = 'in_production', _('في الإنتاج')
        IN_FINISHING = 'in_finishing', _('في التشطيب')
        QUALITY_CHECK = 'quality_check', _('فحص الجودة')
        READY = 'ready', _('جاهز')
        DELIVERED = 'delivered', _('تم التسليم')
        CANCELLED = 'cancelled', _('ملغي')

    class Priority(models.TextChoices):
        LOW = 'low', _('منخفض')
        NORMAL = 'normal', _('عادي')
        HIGH = 'high', _('عالي')
        URGENT = 'urgent', _('عاجل')

    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', _('نسبة مئوية')
        FIXED = 'fixed', _('قيمة ثابتة')

    class PaymentStatus(models.TextChoices):
        UNPAID = 'unpaid', _('غير مدفوع')
        PARTIAL = 'partial', _('مدفوع جزئياً')
        PAID = 'paid', _('مدفوع بالكامل')

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('نقدي')
        BANK = 'bank', _('تحويل بنكي')
        CHEQUE = 'cheque', _('شيك')
        CREDIT = 'credit', _('بطاقة ائتمان')
        LATER = 'later', _('آجل')

    order_number = models.CharField(
        _('رقم الطلب'), max_length=20, unique=True, editable=False
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT,
        related_name='orders', verbose_name=_('العميل')
    )
    quote = models.ForeignKey(
        Quote, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name=_('عرض السعر')
    )
    order_type = models.CharField(
        _('نوع الطلب'), max_length=20,
        choices=OrderType.choices, default=OrderType.NORMAL
    )
    order_date = models.DateTimeField(
        _('تاريخ الطلب'), auto_now_add=True
    )
    delivery_date = models.DateField(_('تاريخ التسليم'))
    status = models.CharField(
        _('الحالة'), max_length=20,
        choices=Status.choices, default=Status.PENDING
    )
    priority = models.CharField(
        _('الأولوية'), max_length=20,
        choices=Priority.choices, default=Priority.NORMAL
    )
    subtotal = models.DecimalField(
        _('المجموع الفرعي'), max_digits=12, decimal_places=2, default=0
    )
    discount_type = models.CharField(
        _('نوع الخصم'), max_length=20,
        choices=DiscountType.choices, blank=True, null=True
    )
    discount_value = models.DecimalField(
        _('قيمة الخصم'), max_digits=12, decimal_places=2, default=0
    )
    tax_percentage = models.DecimalField(
        _('نسبة الضريبة'), max_digits=5, decimal_places=2, default=14
    )
    tax_amount = models.DecimalField(
        _('قيمة الضريبة'), max_digits=12, decimal_places=2, default=0
    )
    shipping_cost = models.DecimalField(
        _('تكلفة الشحن'), max_digits=12, decimal_places=2, default=0
    )
    total = models.DecimalField(
        _('الإجمالي'), max_digits=12, decimal_places=2, default=0
    )
    paid_amount = models.DecimalField(
        _('المبلغ المدفوع'), max_digits=12, decimal_places=2, default=0
    )
    due_amount = models.DecimalField(
        _('المبلغ المتبقي'), max_digits=12, decimal_places=2, default=0
    )
    payment_status = models.CharField(
        _('حالة الدفع'), max_length=20,
        choices=PaymentStatus.choices, default=PaymentStatus.UNPAID
    )
    payment_method = models.CharField(
        _('طريقة الدفع'), max_length=20,
        choices=PaymentMethod.choices, blank=True, null=True
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    internal_notes = models.TextField(
        _('ملاحظات داخلية'), blank=True
    )
    delivery_address = models.TextField(_('عنوان التسليم'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name=_('تم بواسطة')
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        verbose_name = _('طلب')
        verbose_name_plural = _('الطلبات')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.order_number} - {self.customer}'

    @property
    def calculated_discount_amount(self):
        if self.discount_type == 'percentage':
            return self.subtotal * (self.discount_value / 100)
        elif self.discount_type == 'fixed':
            return self.discount_value
        return 0

    def calculate_totals(self):
        self.subtotal = sum(item.total for item in self.items.all())
        discount_amount = self.calculated_discount_amount
        after_discount = self.subtotal - discount_amount
        self.tax_amount = after_discount * (self.tax_percentage / 100)
        self.total = after_discount + self.tax_amount + self.shipping_cost
        self.save(update_fields=['subtotal', 'tax_amount', 'total'])
        return self.total

    def update_payment_status(self):
        if self.subtotal == 0 and self.items.exists():
            self.calculate_totals()
        total_paid = sum(
            p.amount for p in self.payments.all()
        )
        self.paid_amount = total_paid
        self.due_amount = self.total - total_paid
        if total_paid <= 0:
            self.payment_status = self.PaymentStatus.UNPAID
        elif total_paid >= self.total:
            self.payment_status = self.PaymentStatus.PAID
        else:
            self.payment_status = self.PaymentStatus.PARTIAL
        self.save(update_fields=['paid_amount', 'due_amount', 'payment_status'])

    def save(self, *args, **kwargs):
        if not self.order_number:
            year = kwargs.pop('_year', None)
            from django.utils import timezone
            year = year or timezone.now().year
            prefix = f'ORD-{year}-'
            last = Order.objects.filter(
                order_number__startswith=prefix
            ).order_by('order_number').last()
            if last:
                last_num = int(last.order_number.split('-')[-1])
                self.order_number = f'{prefix}{last_num + 1:04d}'
            else:
                self.order_number = f'{prefix}0001'
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    class ItemType(models.TextChoices):
        PRINTING = 'printing', _('طباعة')
        LASER = 'laser', _('ليزر')
        ENGRAVING = 'engraving', _('حفر')
        DESIGN = 'design', _('تصميم')
        MATERIAL = 'material', _('خامات')
        OTHER = 'other', _('أخرى')

    class Unit(models.TextChoices):
        PIECE = 'piece', _('قطعة')
        METER = 'meter', _('متر')
        SQM = 'sqm', _('متر مربع')
        ROLL = 'roll', _('رول')
        SET = 'set', _('طقم')
        HOUR = 'hour', _('ساعة')

    class Status(models.TextChoices):
        PENDING = 'pending', _('قيد الانتظار')
        IN_DESIGN = 'in_design', _('في التصميم')
        IN_PRODUCTION = 'in_production', _('في الإنتاج')
        IN_FINISHING = 'in_finishing', _('في التشطيب')
        COMPLETED = 'completed', _('مكتمل')

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items', verbose_name=_('الطلب')
    )
    item_type = models.CharField(
        _('نوع البند'), max_length=20,
        choices=ItemType.choices, default=ItemType.PRINTING
    )
    description = models.CharField(_('الوصف'), max_length=500)
    material = models.ForeignKey(
        'inventory.Material', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_('الخامة')
    )
    design_file = models.FileField(
        _('ملف التصميم'), upload_to='designs/', blank=True
    )
    quantity = models.IntegerField(_('الكمية'))
    unit = models.CharField(
        _('الوحدة'), max_length=20,
        choices=Unit.choices, default=Unit.PIECE
    )
    unit_price = models.DecimalField(
        _('سعر الوحدة'), max_digits=12, decimal_places=2
    )
    discount_percent = models.DecimalField(
        _('نسبة الخصم'), max_digits=5, decimal_places=2, default=0
    )
    total = models.DecimalField(
        _('الإجمالي'), max_digits=12, decimal_places=2, default=0
    )
    production_notes = models.TextField(_('ملاحظات الإنتاج'), blank=True)
    status = models.CharField(
        _('الحالة'), max_length=20,
        choices=Status.choices, default=Status.PENDING, blank=True
    )
    assigned_to = models.ForeignKey(
        'employees.Employee', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name=_('مسند إلى')
    )
    notes = models.TextField(_('ملاحظات'), blank=True)

    class Meta:
        verbose_name = _('بند الطلب')
        verbose_name_plural = _('بنود الطلب')

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        line_total = self.quantity * self.unit_price
        if self.discount_percent:
            line_total -= line_total * (self.discount_percent / 100)
        self.total = line_total
        super().save(*args, **kwargs)


class OrderPayment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('نقدي')
        BANK = 'bank', _('تحويل بنكي')
        CHEQUE = 'cheque', _('شيك')
        CREDIT = 'credit', _('بطاقة ائتمان')

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='payments', verbose_name=_('الطلب')
    )
    amount = models.DecimalField(
        _('المبلغ'), max_digits=12, decimal_places=2
    )
    payment_date = models.DateField(
        _('تاريخ الدفع'), auto_now_add=True
    )
    payment_method = models.CharField(
        _('طريقة الدفع'), max_length=20,
        choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )
    reference = models.CharField(
        _('مرجع'), max_length=100, blank=True
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name=_('تم بواسطة')
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)

    class Meta:
        verbose_name = _('دفعة')
        verbose_name_plural = _('المدفوعات')
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.order} - {self.amount} - {self.payment_date}'


class DesignFile(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='design_files', verbose_name=_('الطلب')
    )
    file = models.FileField(
        _('الملف'), upload_to='designs/%Y/%m/'
    )
    version = models.IntegerField(_('الإصدار'), default=1)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name=_('تم الرفع بواسطة')
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    uploaded_at = models.DateTimeField(_('تاريخ الرفع'), auto_now_add=True)

    class Meta:
        verbose_name = _('ملف تصميم')
        verbose_name_plural = _('ملفات التصميم')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.order} - v{self.version}'


class DeliveryNote(models.Model):
    class DeliveryStatus(models.TextChoices):
        PARTIAL = 'partial', _('تسليم جزئي')
        FULL = 'full', _('تسليم كامل')

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='delivery_notes', verbose_name=_('الطلب')
    )
    delivered_by = models.CharField(
        _('تم التسليم بواسطة'), max_length=200
    )
    received_by = models.CharField(
        _('استلم'), max_length=200, blank=True
    )
    delivery_date = models.DateTimeField(_('تاريخ التسليم'))
    items_delivered = models.TextField(_('البنود المسلمة'))
    status = models.CharField(
        _('الحالة'), max_length=20,
        choices=DeliveryStatus.choices, default=DeliveryStatus.FULL
    )
    notes = models.TextField(_('ملاحظات'), blank=True)

    class Meta:
        verbose_name = _('مذكرة تسليم')
        verbose_name_plural = _('مذكرات التسليم')
        ordering = ['-delivery_date']

    def __str__(self):
        return f'{self.order} - {self.delivery_date}'
