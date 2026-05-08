from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Customer(models.Model):
    class CustomerType(models.TextChoices):
        INDIVIDUAL = 'individual', _('فرد')
        COMPANY = 'company', _('شركة')

    customer_type = models.CharField(
        _('نوع العميل'), max_length=20,
        choices=CustomerType.choices, default=CustomerType.INDIVIDUAL
    )
    code = models.CharField(
        _('كود العميل'), max_length=20, unique=True, editable=False
    )
    name = models.CharField(
        _('الاسم'), max_length=200, blank=True, unique=True,
        help_text=_('الاسم الأساسي للعميل (اسم الشخص للفرد، أو اسم الشركة للشركة)')
    )
    company_name = models.CharField(
        _('اسم الشركة'), max_length=200, blank=True
    )
    contact_person = models.CharField(
        _('الشخص المسؤول'), max_length=200, blank=True
    )
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    secondary_phone = models.CharField(
        _('هاتف آخر'), max_length=20, blank=True
    )
    email = models.EmailField(_('البريد الإلكتروني'), blank=True)
    address = models.TextField(_('العنوان'), blank=True)
    city = models.CharField(_('المدينة'), max_length=100, blank=True)
    tax_number = models.CharField(
        _('الرقم الضريبي'), max_length=50, blank=True
    )
    credit_limit = models.DecimalField(
        _('الحد الائتماني'), max_digits=12, decimal_places=2, default=0
    )
    current_balance = models.DecimalField(
        _('الرصيد الحالي'), max_digits=12, decimal_places=2, default=0
    )
    notes = models.TextField(_('ملاحظات'), blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name=_('تم بواسطة')
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('آخر تحديث'), auto_now=True)

    class Meta:
        verbose_name = _('عميل')
        verbose_name_plural = _('العملاء')
        ordering = ['-created_at']

    def __str__(self):
        return self.name or self.contact_person or self.company_name or self.phone

    def get_balance_display(self):
        if self.current_balance > 0:
            return _('مدين: %s') % self.current_balance
        elif self.current_balance < 0:
            return _('دائن: %s') % abs(self.current_balance)
        return _('صفر')

    def save(self, *args, **kwargs):
        if not self.code:
            last = Customer.objects.order_by('-id').first()
            last_id = last.id if last else 0
            self.code = f'CUST-{last_id + 1:04d}'
        if not self.name:
            if self.customer_type == 'company' and self.company_name:
                self.name = self.company_name
            elif self.contact_person:
                self.name = self.contact_person
        super().save(*args, **kwargs)


class CustomerContact(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name='contacts', verbose_name=_('العميل')
    )
    name = models.CharField(_('الاسم'), max_length=200)
    phone = models.CharField(_('رقم الهاتف'), max_length=20, blank=True)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True)
    position = models.CharField(_('المسمى الوظيفي'), max_length=100, blank=True)
    is_primary = models.BooleanField(_('جهة اتصال رئيسية'), default=False)

    class Meta:
        verbose_name = _('جهة اتصال')
        verbose_name_plural = _('جهات الاتصال')

    def __str__(self):
        return f'{self.name} - {self.customer}'


class CustomerInteraction(models.Model):
    class InteractionType(models.TextChoices):
        CALL = 'call', _('اتصال هاتفي')
        EMAIL = 'email', _('بريد إلكتروني')
        VISIT = 'visit', _('زيارة')
        WHATSAPP = 'whatsapp', _('واتساب')
        OTHER = 'other', _('أخرى')

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name='interactions', verbose_name=_('العميل')
    )
    interaction_type = models.CharField(
        _('نوع التفاعل'), max_length=20,
        choices=InteractionType.choices
    )
    summary = models.TextField(_('ملخص'))
    details = models.TextField(_('تفاصيل'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        verbose_name=_('تم بواسطة')
    )
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)

    class Meta:
        verbose_name = _('تفاعل')
        verbose_name_plural = _('التفاعلات')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_interaction_type_display()} - {self.customer}'


class CustomerPayment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('نقدي')
        BANK_TRANSFER = 'bank_transfer', _('تحويل بنكي')
        CHEQUE = 'cheque', _('شيك')
        CREDIT_CARD = 'credit_card', _('بطاقة ائتمان')
        OTHER = 'other', _('أخرى')

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name='payments', verbose_name=_('العميل')
    )
    amount = models.DecimalField(
        _('المبلغ'), max_digits=12, decimal_places=2
    )
    payment_date = models.DateField(_('تاريخ الدفع'))
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
        return f'{self.customer} - {self.amount} - {self.payment_date}'
