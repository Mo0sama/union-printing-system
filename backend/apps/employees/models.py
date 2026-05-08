import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.core.validators import validate_file_extension, validate_file_size

User = get_user_model()

DEPARTMENT_CHOICES = [
    ('management', 'إدارة'),
    ('design', 'تصميم'),
    ('printing', 'طباعة'),
    ('finishing', 'تشطيب'),
    ('sales', 'مبيعات'),
    ('warehouse', 'مخزن'),
    ('delivery', 'توصيل'),
]

SALARY_TYPE_CHOICES = [
    ('fixed', 'ثابت'),
    ('hourly', 'بالساعة'),
    ('commission_based', 'عمولة'),
]

ATTENDANCE_STATUS_CHOICES = [
    ('present', 'حاضر'),
    ('absent', 'غائب'),
    ('late', 'متأخر'),
    ('half_day', 'نصف يوم'),
    ('holiday', 'إجازة رسمية'),
    ('leave', 'إجازة'),
]

LEAVE_TYPE_CHOICES = [
    ('annual', 'سنوية'),
    ('sick', 'مرضية'),
    ('emergency', 'طارئة'),
    ('unpaid', 'بدون راتب'),
]

LEAVE_STATUS_CHOICES = [
    ('pending', 'قيد الانتظار'),
    ('approved', 'معتمدة'),
    ('rejected', 'مرفوضة'),
]


def generate_employee_code():
    prefix = 'EMP-'
    last_employee = Employee.objects.filter(
        employee_code__startswith=prefix
    ).order_by('employee_code').last()
    if last_employee:
        try:
            last_num = int(last_employee.employee_code[len(prefix):])
            new_num = last_num + 1
        except (ValueError, IndexError):
            new_num = 1
    else:
        new_num = 1
    return f'{prefix}{new_num:04d}'


class Employee(models.Model):
    employee_code = models.CharField(
        max_length=20, unique=True, verbose_name='كود الموظف'
    )
    full_name = models.CharField(max_length=200, verbose_name='الاسم الكامل')
    full_name_ar = models.CharField(
        max_length=200, blank=True, verbose_name='الاسم بالعربية'
    )
    phone = models.CharField(max_length=20, verbose_name='رقم الهاتف')
    email = models.EmailField(blank=True, verbose_name='البريد الإلكتروني')
    position = models.CharField(max_length=200, verbose_name='المسمى الوظيفي')
    department = models.CharField(
        max_length=50, choices=DEPARTMENT_CHOICES, verbose_name='القسم'
    )
    hire_date = models.DateField(verbose_name='تاريخ التعيين')
    salary_type = models.CharField(
        max_length=50, choices=SALARY_TYPE_CHOICES, verbose_name='نوع الراتب'
    )
    base_salary = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='الراتب الأساسي'
    )
    commission_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name='نسبة العمولة'
    )
    id_number = models.CharField(
        max_length=50, blank=True, verbose_name='رقم الهوية'
    )
    address = models.TextField(blank=True, verbose_name='العنوان')
    emergency_contact = models.CharField(
        max_length=200, blank=True, verbose_name='جهة اتصال طارئة'
    )
    emergency_phone = models.CharField(
        max_length=20, blank=True, verbose_name='هاتف الطوارئ'
    )
    bank_account = models.CharField(
        max_length=100, blank=True, verbose_name='الحساب البنكي'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    photo = models.ImageField(
        upload_to='employees/', blank=True, verbose_name='صورة',
        validators=[validate_file_extension, validate_file_size]
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'موظف'
        verbose_name_plural = 'الموظفين'

    def __str__(self):
        return f'{self.full_name} ({self.employee_code})'

    def save(self, *args, **kwargs):
        if not self.employee_code:
            self.employee_code = generate_employee_code()
        super().save(*args, **kwargs)


class Attendance(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE,
        related_name='attendance', verbose_name='الموظف'
    )
    date = models.DateField(verbose_name='التاريخ')
    check_in = models.TimeField(verbose_name='وقت الحضور')
    check_out = models.TimeField(
        null=True, blank=True, verbose_name='وقت الانصراف'
    )
    status = models.CharField(
        max_length=20, choices=ATTENDANCE_STATUS_CHOICES,
        verbose_name='الحالة'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    recorded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        verbose_name='مسجل بواسطة'
    )

    class Meta:
        ordering = ['-date', '-check_in']
        unique_together = ['employee', 'date']
        verbose_name = 'حضور'
        verbose_name_plural = 'الحضور والانصراف'

    def __str__(self):
        return f'{self.employee} - {self.date} - {self.get_status_display()}'


class EmployeeLeave(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE,
        related_name='leaves', verbose_name='الموظف'
    )
    leave_type = models.CharField(
        max_length=20, choices=LEAVE_TYPE_CHOICES, verbose_name='نوع الإجازة'
    )
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(verbose_name='تاريخ النهاية')
    days_count = models.IntegerField(verbose_name='عدد الأيام')
    reason = models.TextField(verbose_name='السبب')
    status = models.CharField(
        max_length=20, choices=LEAVE_STATUS_CHOICES,
        default='pending', verbose_name='الحالة'
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_leaves', verbose_name='معتمد بواسطة'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='تاريخ الإنشاء'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'إجازة'
        verbose_name_plural = 'الإجازات'

    def __str__(self):
        return f'{self.employee} - {self.get_leave_type_display()} ({self.start_date} - {self.end_date})'

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({'end_date': 'تاريخ النهاية يجب أن يكون بعد تاريخ البداية'})

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            self.days_count = (self.end_date - self.start_date).days + 1
        super().save(*args, **kwargs)


class EmployeeSalary(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE,
        related_name='salaries', verbose_name='الموظف'
    )
    month = models.CharField(
        max_length=7, verbose_name='الشهر (YYYY-MM)'
    )
    base_salary = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='الراتب الأساسي'
    )
    bonuses = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='المكافآت'
    )
    deductions = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='الخصومات'
    )
    commission = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='العمولة'
    )
    overtime = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='الإضافي'
    )
    net_salary = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='صافي الراتب'
    )
    paid = models.BooleanField(default=False, verbose_name='تم الدفع')
    payment_date = models.DateField(
        null=True, blank=True, verbose_name='تاريخ الدفع'
    )
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='تاريخ الإنشاء'
    )

    class Meta:
        ordering = ['-month']
        unique_together = ['employee', 'month']
        verbose_name = 'راتب'
        verbose_name_plural = 'الرواتب'

    def __str__(self):
        return f'{self.employee} - {self.month} - {self.net_salary}'


class EmployeeAdvance(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE,
        related_name='advances', verbose_name='الموظف'
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='المبلغ'
    )
    date = models.DateField(verbose_name='التاريخ')
    reason = models.TextField(blank=True, verbose_name='السبب')
    repaid = models.BooleanField(default=False, verbose_name='تم السداد')
    repayment_date = models.DateField(
        null=True, blank=True, verbose_name='تاريخ السداد'
    )

    class Meta:
        ordering = ['-date']
        verbose_name = 'سلفة'
        verbose_name_plural = 'السلف'

    def __str__(self):
        return f'{self.employee} - {self.amount} - {self.date}'
