from django.conf import settings
from django.db import models
from apps.core.validators import validate_document_file, validate_file_size_10mb


class Department(models.Model):
    name = models.CharField(max_length=200)
    name_ar = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'قسم إنتاج'
        verbose_name_plural = 'أقسام الإنتاج'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name_ar or self.name


class Machine(models.Model):
    class MachineType(models.TextChoices):
        LARGE_FORMAT = 'large_format', 'Large Format'
        OFFSET = 'offset', 'Offset'
        UV = 'uv', 'UV'
        SUBLIMATION = 'sublimation', 'Sublimation'
        LASER = 'laser', 'Laser'
        FINISHING = 'finishing', 'Finishing'
        OTHER = 'other', 'Other'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'نشط'
        MAINTENANCE = 'maintenance', 'صيانة'
        INACTIVE = 'inactive', 'غير نشط'

    name = models.CharField(max_length=200)
    machine_type = models.CharField(max_length=20, choices=MachineType.choices)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='machines')
    model = models.CharField(max_length=200, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'ماكينة'
        verbose_name_plural = 'الماكينات'
        ordering = ['department', 'name']

    def __str__(self):
        return f'{self.name} ({self.get_machine_type_display()})'


class ProductionJob(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد الانتظار'
        IN_PROGRESS = 'in_progress', 'قيد التنفيذ'
        COMPLETED = 'completed', 'مكتمل'
        QUALITY_CHECK = 'quality_check', 'فحص جودة'
        REJECTED = 'rejected', 'مرفوض'
        PAUSED = 'paused', 'متوقف'

    class Priority(models.TextChoices):
        LOW = 'low', 'منخفض'
        NORMAL = 'normal', 'عادي'
        HIGH = 'high', 'عالي'
        URGENT = 'urgent', 'عاجل'

    job_number = models.CharField(max_length=20, unique=True, editable=False)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='production_jobs')
    order_item = models.ForeignKey('orders.OrderItem', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='production_jobs')
    machine = models.ForeignKey(Machine, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_to = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='production_tasks')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    quantity = models.IntegerField()
    completed_quantity = models.IntegerField(default=0)
    rejected_quantity = models.IntegerField(default=0)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'أمر إنتاج'
        verbose_name_plural = 'أوامر الإنتاج'
        ordering = ['-created_at']

    def __str__(self):
        return self.job_number

    def save(self, *args, **kwargs):
        if not self.job_number:
            from django.utils import timezone
            year = timezone.now().year
            prefix = f'PRJ-{year}-'
            last = ProductionJob.objects.filter(job_number__startswith=prefix).order_by('job_number').last()
            if last:
                last_num = int(last.job_number.split('-')[-1])
                self.job_number = f'{prefix}{last_num + 1:04d}'
            else:
                self.job_number = f'{prefix}0001'
        super().save(*args, **kwargs)


class ProductionStage(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'قيد الانتظار'
        IN_PROGRESS = 'in_progress', 'قيد التنفيذ'
        COMPLETED = 'completed', 'مكتمل'
        SKIPPED = 'skipped', 'تم التجاهل'

    production_job = models.ForeignKey(ProductionJob, on_delete=models.CASCADE, related_name='stages')
    stage_name = models.CharField(max_length=200)
    stage_order = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'مرحلة إنتاج'
        verbose_name_plural = 'مراحل الإنتاج'
        ordering = ['production_job', 'stage_order']

    def __str__(self):
        return f'{self.production_job.job_number} - {self.stage_name}'


class QualityCheck(models.Model):
    class Result(models.TextChoices):
        PASSED = 'passed', 'مقبول'
        FAILED = 'failed', 'مرفوض'
        CONDITIONAL = 'conditional', 'معلق بشروط'

    production_job = models.ForeignKey(ProductionJob, on_delete=models.CASCADE, related_name='quality_checks')
    checked_by = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    check_date = models.DateTimeField(auto_now_add=True)
    result = models.CharField(max_length=20, choices=Result.choices)
    defects = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    attachments = models.FileField(upload_to='quality_checks/', blank=True, validators=[validate_document_file, validate_file_size_10mb])

    class Meta:
        verbose_name = 'فحص جودة'
        verbose_name_plural = 'فحوصات الجودة'
        ordering = ['-check_date']

    def __str__(self):
        return f'{self.production_job.job_number} - {self.get_result_display()}'
