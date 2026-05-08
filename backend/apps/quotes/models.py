from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.customers.models import Customer


class Quote(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('مسودة')
        SENT = 'sent', _('مرسل')
        ACCEPTED = 'accepted', _('مقبول')
        REJECTED = 'rejected', _('مرفوض')
        EXPIRED = 'expired', _('منتهي')
        CONVERTED = 'converted', _('محول لطلب')

    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', _('نسبة مئوية')
        FIXED = 'fixed', _('قيمة ثابتة')

    quote_number = models.CharField(
        _('رقم عرض السعر'), max_length=20, unique=True, editable=False
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT,
        related_name='quotes', verbose_name=_('العميل')
    )
    contact_person = models.CharField(
        _('جهة الاتصال'), max_length=200, blank=True
    )
    quote_date = models.DateField(
        _('تاريخ عرض السعر'), auto_now_add=True
    )
    valid_until = models.DateField(_('صلاحية حتى'))
    status = models.CharField(
        _('الحالة'), max_length=20,
        choices=Status.choices, default=Status.DRAFT
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
    total = models.DecimalField(
        _('الإجمالي'), max_digits=12, decimal_places=2, default=0
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    terms_conditions = models.TextField(_('الشروط والأحكام'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name=_('تم بواسطة')
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        verbose_name = _('عرض سعر')
        verbose_name_plural = _('عروض الأسعار')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.quote_number} - {self.customer}'

    def calculate_totals(self):
        self.subtotal = sum(item.total for item in self.items.all())
        if self.discount_type == 'percentage':
            discount_amount = self.subtotal * (self.discount_value / 100)
        elif self.discount_type == 'fixed':
            discount_amount = self.discount_value
        else:
            discount_amount = 0
        after_discount = self.subtotal - discount_amount
        self.tax_amount = after_discount * (self.tax_percentage / 100)
        self.total = after_discount + self.tax_amount
        return self.total

    def save(self, *args, **kwargs):
        if not self.quote_number:
            year = self.quote_date.year if hasattr(self, 'quote_date') and self.quote_date else None
            from django.utils import timezone
            year = year or timezone.now().year
            prefix = f'QTE-{year}-'
            last = Quote.objects.filter(
                quote_number__startswith=prefix
            ).order_by('quote_number').last()
            if last:
                last_num = int(last.quote_number.split('-')[-1])
                self.quote_number = f'{prefix}{last_num + 1:04d}'
            else:
                self.quote_number = f'{prefix}0001'
        super().save(*args, **kwargs)

    def convert_to_order(self):
        from apps.orders.models import Order
        order = Order.objects.create(
            customer=self.customer,
            quote=self,
            contact_person=self.contact_person,
            subtotal=self.subtotal,
            discount_type=self.discount_type,
            discount_value=self.discount_value,
            tax_percentage=self.tax_percentage,
            tax_amount=self.tax_amount,
            total=self.total,
            notes=self.notes,
            created_by=self.created_by,
        )
        for item in self.items.all():
            order.items.create(
                description=item.description,
                quantity=item.quantity,
                unit=item.unit,
                unit_price=item.unit_price,
                discount_percent=item.discount_percent,
                total=item.total,
                notes=item.notes,
            )
        self.status = self.Status.CONVERTED
        self.save()
        return order


class QuoteItem(models.Model):
    class Unit(models.TextChoices):
        PIECE = 'piece', _('قطعة')
        METER = 'meter', _('متر')
        SQM = 'sqm', _('متر مربع')
        ROLL = 'roll', _('رول')
        SET = 'set', _('طقم')
        HOUR = 'hour', _('ساعة')

    quote = models.ForeignKey(
        Quote, on_delete=models.CASCADE,
        related_name='items', verbose_name=_('عرض السعر')
    )
    description = models.CharField(_('الوصف'), max_length=500)
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
    notes = models.TextField(_('ملاحظات'), blank=True)

    class Meta:
        verbose_name = _('بند عرض السعر')
        verbose_name_plural = _('بنود عرض السعر')

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):
        line_total = self.quantity * self.unit_price
        if self.discount_percent:
            line_total -= line_total * (self.discount_percent / 100)
        self.total = line_total
        super().save(*args, **kwargs)
