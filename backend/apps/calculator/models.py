from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name='الاسم (إنجليزي)')
    name_ar = models.CharField(max_length=200, verbose_name='الاسم (عربي)')
    description = models.TextField(blank=True, verbose_name='الوصف')
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class', verbose_name='الأيقونة')
    sort_order = models.IntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='نشط')

    class Meta:
        verbose_name = 'تصنيف خدمة طباعة'
        verbose_name_plural = 'تصنيفات خدمات الطباعة'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name_ar or self.name


class ServiceProduct(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='products', verbose_name='التصنيف')
    name = models.CharField(max_length=200, verbose_name='الاسم (إنجليزي)')
    name_ar = models.CharField(max_length=200, verbose_name='الاسم (عربي)')
    description = models.TextField(blank=True, verbose_name='الوصف')
    image = models.ImageField(upload_to='calculator/services/', blank=True, null=True, verbose_name='الصورة')
    has_options = models.BooleanField(default=False, verbose_name='له خيارات إضافية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')

    class Meta:
        verbose_name = 'منتج طباعة'
        verbose_name_plural = 'منتجات الطباعة'
        ordering = ['category__sort_order', 'name']

    def __str__(self):
        return self.name_ar or self.name

    def get_price_for_quantity(self, quantity):
        tier = self.pricing_tiers.filter(
            qty_from__lte=quantity, qty_to__gte=quantity
        ).first()
        if tier:
            return tier.unit_price
        tier = self.pricing_tiers.filter(qty_to__gte=quantity).order_by('qty_from').first()
        if tier:
            return tier.unit_price
        tier = self.pricing_tiers.order_by('-qty_to').first()
        return tier.unit_price if tier else 0


class PricingTier(models.Model):
    product = models.ForeignKey(ServiceProduct, on_delete=models.CASCADE, related_name='pricing_tiers', verbose_name='المنتج')
    qty_from = models.IntegerField(verbose_name='الكمية من')
    qty_to = models.IntegerField(verbose_name='الكمية إلى')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='سعر الوحدة')

    class Meta:
        verbose_name = 'شريحة سعرية (طباعة)'
        verbose_name_plural = 'الشرائح السعرية (طباعة)'
        ordering = ['product', 'qty_from']

    def __str__(self):
        return f'{self.product.name_ar}: {self.qty_from}-{self.qty_to} = {self.unit_price}'


class GiveawayCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name='الاسم (إنجليزي)')
    name_ar = models.CharField(max_length=200, verbose_name='الاسم (عربي)')
    description = models.TextField(blank=True, verbose_name='الوصف')
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class', verbose_name='الأيقونة')
    sort_order = models.IntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='نشط')

    class Meta:
        verbose_name = 'تصنيف هدية دعائية'
        verbose_name_plural = 'تصنيفات الهدايا الدعائية'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name_ar or self.name


class GiveawayProduct(models.Model):
    category = models.ForeignKey(GiveawayCategory, on_delete=models.CASCADE, related_name='products', verbose_name='التصنيف')
    name = models.CharField(max_length=200, verbose_name='الاسم (إنجليزي)')
    name_ar = models.CharField(max_length=200, verbose_name='الاسم (عربي)')
    description = models.TextField(blank=True, verbose_name='الوصف')
    image = models.ImageField(upload_to='calculator/giveaways/', blank=True, null=True, verbose_name='الصورة')
    has_options = models.BooleanField(default=False, verbose_name='له خيارات إضافية')
    is_active = models.BooleanField(default=True, verbose_name='نشط')

    class Meta:
        verbose_name = 'هدية دعائية'
        verbose_name_plural = 'الهدايا الدعائية'
        ordering = ['category__sort_order', 'name']

    def __str__(self):
        return self.name_ar or self.name

    def get_price_for_quantity(self, quantity, option_id=None):
        if option_id:
            tier = self.pricing_tiers.filter(
                option_id=option_id, qty_from__lte=quantity, qty_to__gte=quantity
            ).first()
            if tier:
                return tier.unit_price
            tier = self.pricing_tiers.filter(
                option_id=option_id, qty_to__gte=quantity
            ).order_by('qty_from').first()
            if tier:
                return tier.unit_price
            fallback = self.pricing_tiers.filter(option_id=option_id).order_by('-qty_to').first()
            if fallback:
                return fallback.unit_price
        tier = self.pricing_tiers.filter(
            option__isnull=True, qty_from__lte=quantity, qty_to__gte=quantity
        ).first()
        if tier:
            return tier.unit_price
        tier = self.pricing_tiers.filter(option__isnull=True, qty_to__gte=quantity).order_by('qty_from').first()
        if tier:
            return tier.unit_price
        tier = self.pricing_tiers.filter(option__isnull=True).order_by('-qty_to').first()
        return tier.unit_price if tier else 0


class GiveawayOption(models.Model):
    product = models.ForeignKey(GiveawayProduct, on_delete=models.CASCADE, related_name='options', verbose_name='المنتج')
    name = models.CharField(max_length=200, verbose_name='الاسم (إنجليزي)')
    name_ar = models.CharField(max_length=200, verbose_name='الاسم (عربي)')
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='تعديل السعر')
    sort_order = models.IntegerField(default=0, verbose_name='الترتيب')

    class Meta:
        verbose_name = 'خيار إضافي'
        verbose_name_plural = 'الخيارات الإضافية'
        ordering = ['product', 'sort_order']

    def __str__(self):
        return self.name_ar or self.name


class GiveawayPricingTier(models.Model):
    product = models.ForeignKey(GiveawayProduct, on_delete=models.CASCADE, related_name='pricing_tiers', verbose_name='المنتج')
    option = models.ForeignKey(GiveawayOption, on_delete=models.SET_NULL, null=True, blank=True, related_name='pricing_tiers', verbose_name='الخيار')
    qty_from = models.IntegerField(verbose_name='الكمية من')
    qty_to = models.IntegerField(verbose_name='الكمية إلى')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='سعر الوحدة')

    class Meta:
        verbose_name = 'شريحة سعرية (هدية)'
        verbose_name_plural = 'الشرائح السعرية (هدية)'
        ordering = ['product', 'qty_from']

    def __str__(self):
        return f'{self.product.name_ar}: {self.qty_from}-{self.qty_to} = {self.unit_price}'


class CalculatorQuote(models.Model):
    class QuoteType(models.TextChoices):
        PRINTING = 'printing', 'طباعة'
        GIVEAWAY = 'giveaway', 'هدايا دعائية'
        MIXED = 'mixed', 'مختلط'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        SUBMITTED = 'submitted', 'مُرسل'
        APPROVED = 'approved', 'مقبول'
        REJECTED = 'rejected', 'مرفوض'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='calculator_quotes', verbose_name='المستخدم'
    )
    contact_name = models.CharField(max_length=200, verbose_name='اسم جهة الاتصال')
    contact_email = models.EmailField(verbose_name='البريد الإلكتروني')
    contact_phone = models.CharField(max_length=50, verbose_name='رقم الهاتف')
    company = models.CharField(max_length=200, blank=True, verbose_name='الشركة')
    quote_number = models.CharField(max_length=50, unique=True, verbose_name='رقم عرض السعر')
    quote_type = models.CharField(max_length=20, choices=QuoteType.choices, default=QuoteType.PRINTING, verbose_name='النوع')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='المجموع الفرعي')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='نسبة الخصم')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='قيمة الخصم')
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=14, verbose_name='نسبة الضريبة')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='قيمة الضريبة')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='الإجمالي')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, verbose_name='الحالة')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        verbose_name = 'عرض سعر عميل'
        verbose_name_plural = 'عروض أسعار العملاء'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.quote_number} - {self.contact_name}'

    def calculate_totals(self):
        items = self.items.all()
        self.subtotal = sum(item.line_total for item in items)
        after_discount = self.subtotal * (1 - self.discount_percent / 100)
        self.discount_amount = self.subtotal - after_discount
        self.tax_amount = after_discount * (self.tax_percent / 100)
        self.total = after_discount + self.tax_amount

    def save(self, *args, **kwargs):
        if not self.quote_number:
            last = CalculatorQuote.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.quote_number = f'CLQ-{next_id:05d}'
        super().save(*args, **kwargs)


class CalculatorQuoteItem(models.Model):
    class ProductType(models.TextChoices):
        SERVICE = 'service', 'خدمة طباعة'
        GIVEAWAY = 'giveaway', 'هدية دعائية'

    quote = models.ForeignKey(CalculatorQuote, on_delete=models.CASCADE, related_name='items', verbose_name='عرض السعر')
    product_type = models.CharField(max_length=20, choices=ProductType.choices, verbose_name='نوع المنتج')
    category_name = models.CharField(max_length=200, verbose_name='اسم التصنيف')
    product_name = models.CharField(max_length=200, verbose_name='اسم المنتج')
    option_name = models.CharField(max_length=200, blank=True, verbose_name='الخيار')
    quantity = models.IntegerField(validators=[MinValueValidator(1)], verbose_name='الكمية')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='سعر الوحدة')
    line_total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='الإجمالي')

    class Meta:
        verbose_name = 'بند عرض سعر عميل'
        verbose_name_plural = 'بنود عروض أسعار العملاء'

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
