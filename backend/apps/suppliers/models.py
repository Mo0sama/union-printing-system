from django.conf import settings
from django.db import models


class Supplier(models.Model):
    code = models.CharField(max_length=20, unique=True, editable=False)
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    secondary_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    supply_type = models.CharField(max_length=100, blank=True)
    tax_number = models.CharField(max_length=50, blank=True)
    payment_terms = models.CharField(max_length=200, blank=True)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مورد'
        verbose_name_plural = 'الموردين'
        ordering = ['company_name']

    def __str__(self):
        return f'{self.code} - {self.company_name}'

    def save(self, *args, **kwargs):
        if not self.code:
            last = Supplier.objects.order_by('-id').first()
            last_id = last.id if last else 0
            self.code = f'SUP-{last_id + 1:04d}'
        super().save(*args, **kwargs)


class PurchaseOrder(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        SENT = 'sent', 'مرسل'
        CONFIRMED = 'confirmed', 'مؤكد'
        RECEIVED = 'received', 'مستلم'
        CANCELLED = 'cancelled', 'ملغي'

    po_number = models.CharField(max_length=20, unique=True, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    order_date = models.DateField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=14)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'أمر شراء'
        verbose_name_plural = 'أوامر الشراء'
        ordering = ['-created_at']

    def __str__(self):
        return self.po_number

    def save(self, *args, **kwargs):
        if not self.po_number:
            from django.utils import timezone
            year = timezone.now().year
            prefix = f'PO-{year}-'
            last = PurchaseOrder.objects.filter(po_number__startswith=prefix).order_by('po_number').last()
            if last:
                last_num = int(last.po_number.split('-')[-1])
                self.po_number = f'{prefix}{last_num + 1:04d}'
            else:
                self.po_number = f'{prefix}0001'
        super().save(*args, **kwargs)


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey('inventory.Material', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    received_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'بند أمر شراء'
        verbose_name_plural = 'بنود أمر الشراء'

    def __str__(self):
        return f'{self.purchase_order.po_number} - {self.material}'


class SupplierPayment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'نقدي'
        BANK_TRANSFER = 'bank_transfer', 'تحويل بنكي'
        CHEQUE = 'cheque', 'شيك'
        CREDIT_CARD = 'credit_card', 'بطاقة ائتمان'
        OTHER = 'other', 'أخرى'

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments')
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دفعة مورد'
        verbose_name_plural = 'دفعات الموردين'
        ordering = ['-payment_date']

    def __str__(self):
        return f'{self.supplier} - {self.amount} - {self.payment_date}'
