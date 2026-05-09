from django.contrib.auth import get_user_model
from django.db import models

from .validators import validate_file_extension, validate_file_size

User = get_user_model()


class CompanySetting(models.Model):
    LANGUAGE_CHOICES = [
        ('ar', 'Arabic'),
        ('en', 'English'),
    ]

    company_name = models.CharField(max_length=200, default='UNION FOR DIGITAL PRINTING')
    logo = models.ImageField(upload_to='company/', blank=True, null=True, validators=[validate_file_extension, validate_file_size])
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    tax_number = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=10, default='EGP')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='ar')
    date_format = models.CharField(max_length=50, default='Y-m-d')
    timezone = models.CharField(max_length=50, default='Africa/Cairo')
    default_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=25.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Setting'
        verbose_name_plural = 'Company Settings'

    def __str__(self):
        return self.company_name

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(pk=1, defaults={'company_name': 'UNION FOR DIGITAL PRINTING'})
        return obj


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField(null=True, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"


class Lookup(models.Model):
    class Type(models.TextChoices):
        MATERIAL_UNIT = 'material_unit', 'وحدات القياس'
        PAYMENT_METHOD = 'payment_method', 'أنواع الدفع'
        ORDER_TYPE = 'order_type', 'أنواع الطلبات'
        MACHINE_TYPE = 'machine_type', 'أنواع الماكينات'
        EMPLOYEE_DEPT = 'employee_dept', 'أقسام الموظفين'
        SUPPLIER_TYPE = 'supplier_type', 'أنواع الموردين'
        CUSTOMER_TYPE = 'customer_type', 'أنواع العملاء'
        VAT = 'vat', 'الضرائب'

        # Order-related
        ORDER_STATUS = 'order_status', 'حالات الطلبات'
        ORDER_PRIORITY = 'order_priority', 'أولويات الطلبات'
        ORDER_ITEM_TYPE = 'order_item_type', 'أنواع بنود الطلب'
        ORDER_ITEM_STATUS = 'order_item_status', 'حالات بنود الطلب'
        UNIT = 'unit', 'وحدات القياس'
        DISCOUNT_TYPE = 'discount_type', 'أنواع الخصم'
        DELIVERY_NOTE_STATUS = 'delivery_note_status', 'حالات مذكرات التسليم'

        # Production-related
        PRODUCTION_JOB_STATUS = 'production_job_status', 'حالات أوامر الإنتاج'
        PRODUCTION_STAGE_STATUS = 'production_stage_status', 'حالات مراحل الإنتاج'
        QUALITY_CHECK_RESULT = 'quality_check_result', 'نتائج فحص الجودة'
        MACHINE_STATUS = 'machine_status', 'حالات الماكينات'

        # Sales-related
        QUOTE_STATUS = 'quote_status', 'حالات عروض الأسعار'

        # Inventory
        STOCK_MOVEMENT_TYPE = 'stock_movement_type', 'أنواع الحركات المخزنية'

        # POS
        POS_SESSION_STATUS = 'pos_session_status', 'حالات جلسات البيع'
        POS_SALE_STATUS = 'pos_sale_status', 'حالات فواتير البيع'
        POS_ITEM_TYPE = 'pos_item_type', 'أنواع بنود الفواتير'

        # Purchasing
        PURCHASE_ORDER_STATUS = 'purchase_order_status', 'حالات أوامر الشراء'

        # CRM
        INTERACTION_TYPE = 'interaction_type', 'أنواع التفاعلات'
        CUSTOMER_PAYMENT_METHOD = 'customer_payment_method', 'طرق دفع العملاء'

        # HR
        LEAVE_TYPE = 'leave_type', 'أنواع الإجازات'
        LEAVE_STATUS = 'leave_status', 'حالات الإجازات'
        ATTENDANCE_STATUS = 'attendance_status', 'حالات الحضور'
        EMPLOYEE_SALARY_TYPE = 'employee_salary_type', 'أنواع الرواتب'

    type = models.CharField(max_length=30, choices=Type.choices, verbose_name='النوع')
    code = models.CharField(max_length=50, verbose_name='الكود')
    name = models.CharField(max_length=200, verbose_name='الاسم (إنجليزي)', blank=True)
    name_ar = models.CharField(max_length=200, verbose_name='الاسم (عربي)')
    sort_order = models.IntegerField(default=0, verbose_name='الترتيب')
    is_active = models.BooleanField(default=True, verbose_name='نشط')

    class Meta:
        verbose_name = 'إعدادات متقدمة'
        verbose_name_plural = 'الإعدادات المتقدمة'
        ordering = ['type', 'sort_order']
        unique_together = [('type', 'code')]

    def __str__(self):
        return self.name_ar or self.name


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order', 'طلب'),
        ('production', 'إنتاج'),
        ('payment', 'دفعة'),
        ('inventory', 'مخزون'),
        ('quote', 'عرض سعر'),
        ('system', 'النظام'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_notification_type_display()} - {self.title}'


class SystemLabel(models.Model):
    key = models.CharField(max_length=200, unique=True, verbose_name='المفتاح')
    value_ar = models.TextField(verbose_name='النص (عربي)', blank=True)
    app_label = models.CharField(max_length=50, verbose_name='التطبيق', blank=True, db_index=True)
    description = models.TextField(verbose_name='الوصف', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='مفعل')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تسمية النظام'
        verbose_name_plural = 'تسميات النظام'
        ordering = ['app_label', 'key']

    def __str__(self):
        return f'{self.key}: {self.value_ar or "(افتراضي)"}'


class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/', validators=[validate_file_extension, validate_file_size])
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.model_name}#{self.object_id} - {self.file.name}"
