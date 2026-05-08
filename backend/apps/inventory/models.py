from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'تصنيف'
        verbose_name_plural = 'التصنيفات'

    def __str__(self):
        return self.name_ar or self.name


class Material(models.Model):
    class Unit(models.TextChoices):
        PIECE = 'piece', 'قطعة'
        METER = 'meter', 'متر'
        SQM = 'sqm', 'متر مربع'
        ROLL = 'roll', 'رول'
        KG = 'kg', 'كجم'
        LITER = 'liter', 'لتر'
        BOX = 'box', 'كرتونة'

    code = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='materials')
    unit = models.CharField(max_length=20, choices=Unit.choices)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    current_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    minimum_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'خامة'
        verbose_name_plural = 'الخامات'
        ordering = ['name']

    def __str__(self):
        return f'{self.code} - {self.name_ar or self.name}'

    def save(self, *args, **kwargs):
        if not self.code:
            last = Material.objects.order_by('-id').first()
            last_id = last.id if last else 0
            self.code = f'MAT-{last_id + 1:04d}'
        super().save(*args, **kwargs)


class Batch(models.Model):
    batch_number = models.CharField(max_length=50, unique=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='batches')
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    remaining_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Batch'
        verbose_name_plural = 'Batches'

    def __str__(self):
        return f'{self.batch_number} - {self.material}'


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        PURCHASE_IN = 'purchase_in', 'مشتريات (وارد)'
        RETURN_IN = 'return_in', 'مرتجع (وارد)'
        SALE_OUT = 'sale_out', 'مبيعات (صادر)'
        USAGE_OUT = 'usage_out', 'استخدام (صادر)'
        DAMAGE_OUT = 'damage_out', 'تالف (صادر)'
        TRANSFER_OUT = 'transfer_out', 'تحويل (صادر)'
        ADJUSTMENT_OUT = 'adjustment_out', 'تسوية (صادر)'
        ADJUSTMENT_IN = 'adjustment_in', 'تسوية (وارد)'
        PRODUCTION_OUT = 'production_out', 'إنتاج (صادر)'

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='stock_movements')
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True)
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reference_type = models.CharField(max_length=50, null=True, blank=True)
    reference_id = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'حركة مخزنية'
        verbose_name_plural = 'الحركات المخزنية'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.material} - {self.get_movement_type_display()} - {self.quantity}'
