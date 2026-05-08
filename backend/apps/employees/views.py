from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import date, timedelta, datetime
from .models import (Employee, Attendance, EmployeeLeave, EmployeeSalary,
                     EmployeeAdvance)
from .forms import (EmployeeForm, AttendanceForm, BulkAttendanceForm,
                    LeaveForm, SalaryForm, AdvanceForm)
from django.http import JsonResponse


@login_required
def employee_list(request):
    search = request.GET.get('search', '')
    department = request.GET.get('department', '')
    status = request.GET.get('status', '')

    employees = Employee.objects.all()

    if search:
        employees = employees.filter(
            Q(full_name__icontains=search) |
            Q(full_name_ar__icontains=search) |
            Q(employee_code__icontains=search) |
            Q(phone__icontains=search) |
            Q(position__icontains=search)
        )
    if department:
        employees = employees.filter(department=department)
    if status == 'active':
        employees = employees.filter(is_active=True)
    elif status == 'inactive':
        employees = employees.filter(is_active=False)

    department_choices = Employee.DEPARTMENT_CHOICES if hasattr(Employee, 'DEPARTMENT_CHOICES') else []
    from .models import DEPARTMENT_CHOICES
    context = {
        'employees': employees,
        'search': search,
        'department': department,
        'status': status,
        'department_choices': DEPARTMENT_CHOICES,
        'title': 'الموظفين',
    }
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    attendances = employee.attendance.all()[:30]
    leaves = employee.leaves.all()[:20]
    salaries = employee.salaries.all()[:12]
    advances = employee.advances.all()[:12]

    context = {
        'employee': employee,
        'attendances': attendances,
        'leaves': leaves,
        'salaries': salaries,
        'advances': advances,
        'title': f'{employee.full_name}',
    }
    return render(request, 'employees/employee_detail.html', context)


@login_required
@permission_required('employees.add_employee', raise_exception=True)
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الموظف بنجاح')
            return redirect('employees:employee_list')
    else:
        form = EmployeeForm()
    context = {
        'form': form,
        'title': 'إضافة موظف جديد',
    }
    return render(request, 'employees/employee_form.html', context)


@login_required
@permission_required('employees.change_employee', raise_exception=True)
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات الموظف بنجاح')
            return redirect('employees:employee_detail', pk=employee.pk)
    else:
        form = EmployeeForm(instance=employee)
    context = {
        'form': form,
        'employee': employee,
        'title': f'تعديل: {employee.full_name}',
    }
    return render(request, 'employees/employee_form.html', context)


@login_required
@permission_required('employees.delete_employee', raise_exception=True)
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'تم حذف الموظف بنجاح')
        return redirect('employees:employee_list')
    context = {
        'employee': employee,
        'title': 'حذف موظف',
    }
    return render(request, 'employees/employee_confirm_delete.html', context)


@login_required
def attendance_list(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    employee_id = request.GET.get('employee', '')
    status_filter = request.GET.get('status', '')

    attendances = Attendance.objects.select_related('employee', 'recorded_by').all()

    if date_from:
        attendances = attendances.filter(date__gte=date_from)
    if date_to:
        attendances = attendances.filter(date__lte=date_to)
    if employee_id:
        attendances = attendances.filter(employee_id=employee_id)
    if status_filter:
        attendances = attendances.filter(status=status_filter)

    from .models import ATTENDANCE_STATUS_CHOICES
    context = {
        'attendances': attendances,
        'date_from': date_from,
        'date_to': date_to,
        'employee_id': int(employee_id) if employee_id else '',
        'status_filter': status_filter,
        'employees': Employee.objects.filter(is_active=True),
        'attendance_status_choices': ATTENDANCE_STATUS_CHOICES,
        'title': 'سجل الحضور والانصراف',
    }
    return render(request, 'employees/attendance_list.html', context)


@login_required
@permission_required('employees.add_attendance', raise_exception=True)
def mark_attendance(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            employee_id = request.POST.get('employee_id')
            att_date = request.POST.get('date')
            check_in = request.POST.get('check_in')
            check_out = request.POST.get('check_out', '')
            status_val = request.POST.get('status', 'present')
            notes = request.POST.get('notes', '')

            employee = get_object_or_404(Employee, pk=employee_id)
            attendance, created = Attendance.objects.update_or_create(
                employee=employee,
                date=att_date,
                defaults={
                    'check_in': check_in,
                    'check_out': check_out if check_out else None,
                    'status': status_val,
                    'notes': notes,
                    'recorded_by': request.user,
                }
            )
            return JsonResponse({
                'success': True,
                'created': created,
                'id': attendance.id,
            })

        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.recorded_by = request.user
            attendance.save()
            messages.success(request, 'تم تسجيل الحضور بنجاح')
            return redirect('employees:attendance_list')
    else:
        form = AttendanceForm()

    context = {
        'form': form,
        'title': 'تسجيل حضور',
    }
    return render(request, 'employees/attendance_form.html', context)


@login_required
@permission_required('employees.add_attendance', raise_exception=True)
def mark_bulk_attendance(request):
    employees = Employee.objects.filter(is_active=True)
    today = date.today()

    if request.method == 'POST':
        att_date = request.POST.get('date')
        for emp in employees:
            check_in = request.POST.get(f'check_in_{emp.id}', '')
            check_out = request.POST.get(f'check_out_{emp.id}', '')
            status_val = request.POST.get(f'status_{emp.id}', 'absent')
            notes = request.POST.get(f'notes_{emp.id}', '')

            if status_val != 'absent' or check_in:
                Attendance.objects.update_or_create(
                    employee=emp,
                    date=att_date,
                    defaults={
                        'check_in': check_in if check_in else '09:00:00',
                        'check_out': check_out if check_out else None,
                        'status': status_val,
                        'notes': notes,
                        'recorded_by': request.user,
                    }
                )
        messages.success(request, 'تم تسجيل الحضور للجميع بنجاح')
        return redirect('employees:attendance_list')

    form = BulkAttendanceForm(initial={'date': today})
    context = {
        'form': form,
        'employees': employees,
        'today': today,
        'title': 'تسجيل حضور جماعي',
    }
    return render(request, 'employees/attendance_bulk_form.html', context)


@login_required
def leave_list(request):
    status_filter = request.GET.get('status', '')
    employee_id = request.GET.get('employee', '')

    leaves = EmployeeLeave.objects.select_related('employee', 'approved_by').all()

    if status_filter:
        leaves = leaves.filter(status=status_filter)
    if employee_id:
        leaves = leaves.filter(employee_id=employee_id)

    context = {
        'leaves': leaves,
        'status_filter': status_filter,
        'employee_id': int(employee_id) if employee_id else '',
        'employees': Employee.objects.filter(is_active=True),
        'title': 'الإجازات',
    }
    return render(request, 'employees/leave_list.html', context)


@login_required
@permission_required('employees.add_employeeleave', raise_exception=True)
def leave_create(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save()
            messages.success(request, 'تم تقديم طلب الإجازة بنجاح')
            return redirect('employees:leave_list')
    else:
        form = LeaveForm()
    context = {
        'form': form,
        'title': 'طلب إجازة جديد',
    }
    return render(request, 'employees/leave_form.html', context)


@login_required
@permission_required('employees.change_employeeleave', raise_exception=True)
def leave_approve(request, pk):
    leave = get_object_or_404(EmployeeLeave, pk=pk)
    action = request.GET.get('action', 'approved')
    if action in ['approved', 'rejected']:
        leave.status = action
        leave.approved_by = request.user
        leave.save()
        msg = 'تم اعتماد الإجازة' if action == 'approved' else 'تم رفض الإجازة'
        messages.success(request, msg)
    return redirect('employees:leave_list')


@login_required
def salary_list(request):
    month = request.GET.get('month', '')
    paid_filter = request.GET.get('paid', '')
    employee_id = request.GET.get('employee', '')

    salaries = EmployeeSalary.objects.select_related('employee').all()

    if month:
        salaries = salaries.filter(month=month)
    if paid_filter in ['true', 'false']:
        salaries = salaries.filter(paid=(paid_filter == 'true'))
    if employee_id:
        salaries = salaries.filter(employee_id=employee_id)

    total_net = salaries.aggregate(
        total=Coalesce(Sum('net_salary'), Value(0), output_field=DecimalField())
    )['total']
    total_paid = salaries.filter(paid=True).aggregate(
        total=Coalesce(Sum('net_salary'), Value(0), output_field=DecimalField())
    )['total']
    total_unpaid = salaries.filter(paid=False).aggregate(
        total=Coalesce(Sum('net_salary'), Value(0), output_field=DecimalField())
    )['total']

    months = EmployeeSalary.objects.values_list('month', flat=True).distinct().order_by('-month')

    context = {
        'salaries': salaries,
        'month': month,
        'paid_filter': paid_filter,
        'employee_id': int(employee_id) if employee_id else '',
        'employees': Employee.objects.filter(is_active=True),
        'months': months,
        'total_net': total_net,
        'total_paid': total_paid,
        'total_unpaid': total_unpaid,
        'title': 'الرواتب',
    }
    return render(request, 'employees/salary_list.html', context)


@login_required
@permission_required('employees.add_employeesalary', raise_exception=True)
def salary_generate(request):
    if request.method == 'POST':
        month = request.POST.get('month', '')
        if not month:
            messages.error(request, 'يرجى تحديد الشهر')
            return redirect('employees:salary_list')

        employees = Employee.objects.filter(is_active=True)
        count = 0
        for emp in employees:
            _, created = EmployeeSalary.objects.get_or_create(
                employee=emp,
                month=month,
                defaults={
                    'base_salary': emp.base_salary,
                    'bonuses': 0,
                    'deductions': 0,
                    'commission': 0,
                    'overtime': 0,
                    'net_salary': emp.base_salary,
                }
            )
            if created:
                count += 1
        messages.success(request, f'تم إنشاء {count} راتب لشهر {month}')
    return redirect('employees:salary_list')


@login_required
@permission_required('employees.change_employeesalary', raise_exception=True)
def salary_edit(request, pk):
    salary = get_object_or_404(EmployeeSalary, pk=pk)
    if request.method == 'POST':
        form = SalaryForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الراتب بنجاح')
            return redirect('employees:salary_list')
    else:
        form = SalaryForm(instance=salary)
    context = {
        'form': form,
        'salary': salary,
        'title': f'تعديل راتب: {salary.employee}',
    }
    return render(request, 'employees/salary_form.html', context)


@login_required
@permission_required('employees.change_employeesalary', raise_exception=True)
def salary_pay(request, pk):
    salary = get_object_or_404(EmployeeSalary, pk=pk)
    if request.method == 'POST':
        salary.paid = True
        salary.payment_date = date.today()
        salary.save()
        messages.success(request, f'تم دفع راتب {salary.employee} بنجاح')
    return redirect('employees:salary_list')


@login_required
def advance_list(request):
    employee_id = request.GET.get('employee', '')
    repaid_filter = request.GET.get('repaid', '')

    advances = EmployeeAdvance.objects.select_related('employee').all()

    if employee_id:
        advances = advances.filter(employee_id=employee_id)
    if repaid_filter in ['true', 'false']:
        advances = advances.filter(repaid=(repaid_filter == 'true'))

    total_advances = advances.aggregate(
        total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
    )['total']

    context = {
        'advances': advances,
        'employee_id': int(employee_id) if employee_id else '',
        'repaid_filter': repaid_filter,
        'employees': Employee.objects.filter(is_active=True),
        'total_advances': total_advances,
        'title': 'السلف',
    }
    return render(request, 'employees/advance_list.html', context)


@login_required
@permission_required('employees.add_employeeadvance', raise_exception=True)
def advance_create(request):
    if request.method == 'POST':
        form = AdvanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تسجيل السلفة بنجاح')
            return redirect('employees:advance_list')
    else:
        form = AdvanceForm()
    context = {
        'form': form,
        'title': 'سلفة جديدة',
    }
    return render(request, 'employees/advance_form.html', context)


@login_required
def payroll_report(request):
    month = request.GET.get('month', '')
    if not month:
        month = date.today().strftime('%Y-%m')

    salaries = EmployeeSalary.objects.filter(month=month).select_related('employee')
    summary = salaries.aggregate(
        total_base=Coalesce(Sum('base_salary'), Value(0), output_field=DecimalField()),
        total_bonuses=Coalesce(Sum('bonuses'), Value(0), output_field=DecimalField()),
        total_deductions=Coalesce(Sum('deductions'), Value(0), output_field=DecimalField()),
        total_commission=Coalesce(Sum('commission'), Value(0), output_field=DecimalField()),
        total_overtime=Coalesce(Sum('overtime'), Value(0), output_field=DecimalField()),
        total_net=Coalesce(Sum('net_salary'), Value(0), output_field=DecimalField()),
    )

    context = {
        'salaries': salaries,
        'month': month,
        'summary': summary,
        'title': 'تقرير الرواتب',
    }
    return render(request, 'employees/payroll_report.html', context)
