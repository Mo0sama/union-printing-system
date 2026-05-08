from django.contrib import admin
from .models import Employee, Attendance, EmployeeLeave, EmployeeSalary, EmployeeAdvance


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_code', 'full_name', 'department', 'position',
                    'salary_type', 'base_salary', 'is_active']
    list_filter = ['department', 'salary_type', 'is_active']
    search_fields = ['full_name', 'full_name_ar', 'employee_code', 'phone', 'email']
    readonly_fields = ['employee_code', 'created_at', 'updated_at']
    fieldsets = [
        ('معلومات أساسية', {
            'fields': ['employee_code', 'full_name', 'full_name_ar', 'phone', 'email']
        }),
        ('الوظيفة', {
            'fields': ['position', 'department', 'hire_date', 'is_active']
        }),
        ('الراتب', {
            'fields': ['salary_type', 'base_salary', 'commission_percentage']
        }),
        ('معلومات شخصية', {
            'fields': ['id_number', 'address', 'emergency_contact',
                       'emergency_phone', 'bank_account', 'photo']
        }),
        ('ملاحظات', {
            'fields': ['notes']
        }),
        ('تواريخ', {
            'fields': ['created_at', 'updated_at']
        }),
    ]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status']
    list_filter = ['status', 'date']
    search_fields = ['employee__full_name', 'employee__employee_code']
    date_hierarchy = 'date'


@admin.register(EmployeeLeave)
class EmployeeLeaveAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date',
                    'days_count', 'status']
    list_filter = ['leave_type', 'status']
    search_fields = ['employee__full_name', 'employee__employee_code']
    date_hierarchy = 'start_date'


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'base_salary', 'bonuses',
                    'deductions', 'net_salary', 'paid']
    list_filter = ['paid', 'month']
    search_fields = ['employee__full_name', 'employee__employee_code']


@admin.register(EmployeeAdvance)
class EmployeeAdvanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'amount', 'date', 'repaid']
    list_filter = ['repaid']
    search_fields = ['employee__full_name', 'employee__employee_code']
