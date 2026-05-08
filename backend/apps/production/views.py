import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import app_permission_required
from django.db.models import Avg, Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DepartmentForm, MachineForm, ProductionJobForm, ProductionStageForm, QualityCheckForm
from .models import Department, Machine, ProductionJob, ProductionStage, QualityCheck


@app_permission_required('production_view')
def production_dashboard(request):
    department_id = request.GET.get('department')
    departments = Department.objects.all()
    jobs = ProductionJob.objects.select_related('department', 'machine', 'assigned_to', 'order')

    if department_id:
        jobs = jobs.filter(department_id=department_id)

    status_groups = {
        'pending': jobs.filter(status='pending'),
        'in_progress': jobs.filter(status='in_progress'),
        'quality_check': jobs.filter(status='quality_check'),
        'completed': jobs.filter(status='completed'),
        'rejected': jobs.filter(status='rejected'),
        'paused': jobs.filter(status='paused'),
    }

    context = {
        'departments': departments,
        'status_groups': status_groups,
        'selected_department': int(department_id) if department_id else None,
        'title': 'لوحة الإنتاج',
    }
    return render(request, 'production/production_dashboard.html', context)


@app_permission_required('production_view')
def production_job_list(request):
    jobs = ProductionJob.objects.select_related('department', 'machine', 'assigned_to', 'order').all()
    department_id = request.GET.get('department')
    status = request.GET.get('status')
    machine_id = request.GET.get('machine')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('q')

    if department_id:
        jobs = jobs.filter(department_id=department_id)
    if status:
        jobs = jobs.filter(status=status)
    if machine_id:
        jobs = jobs.filter(machine_id=machine_id)
    if date_from:
        jobs = jobs.filter(created_at__date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        jobs = jobs.filter(created_at__date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())
    if search:
        jobs = jobs.filter(
            Q(job_number__icontains=search) |
            Q(order__order_number__icontains=search) |
            Q(notes__icontains=search)
        )

    departments = Department.objects.all()
    machines = Machine.objects.filter(status='active')

    context = {
        'jobs': jobs,
        'departments': departments,
        'machines': machines,
        'title': 'أوامر الإنتاج',
    }
    return render(request, 'production/production_job_list.html', context)


@app_permission_required('production_view')
def production_job_detail(request, pk):
    job = get_object_or_404(ProductionJob.objects.select_related(
        'department', 'machine', 'assigned_to', 'order', 'created_by'
    ), pk=pk)
    stages = job.stages.all()
    quality_checks = job.quality_checks.all()

    context = {
        'job': job,
        'stages': stages,
        'quality_checks': quality_checks,
        'title': f'أمر إنتاج - {job.job_number}',
    }
    return render(request, 'production/production_job_detail.html', context)


@app_permission_required('production_create')
def production_job_create(request):
    order_id = request.GET.get('order')
    initial = {}
    if order_id:
        initial['order'] = order_id

    if request.method == 'POST':
        form = ProductionJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.created_by = request.user
            job.save()
            messages.success(request, 'تم إنشاء أمر الإنتاج بنجاح')
            return redirect('production:production_job_detail', pk=job.pk)
    else:
        form = ProductionJobForm(initial=initial)

    from apps.employees.models import Employee
    context = {
        'form': form,
        'title': 'إنشاء أمر إنتاج',
        'departments': Department.objects.all(),
        'machines': Machine.objects.filter(status='active'),
        'employees': Employee.objects.filter(is_active=True),
    }
    return render(request, 'production/production_job_form.html', context)


@app_permission_required('production_edit')
def production_job_edit(request, pk):
    job = get_object_or_404(ProductionJob, pk=pk)
    if request.method == 'POST':
        form = ProductionJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث أمر الإنتاج بنجاح')
            return redirect('production:production_job_detail', pk=job.pk)
    else:
        form = ProductionJobForm(instance=job)

    context = {'form': form, 'job': job, 'title': 'تعديل أمر إنتاج'}
    return render(request, 'production/production_job_form.html', context)


@app_permission_required('production_edit')
def update_job_status(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    job = get_object_or_404(ProductionJob, pk=pk)
    data = json.loads(request.body)
    new_status = data.get('status')

    valid_statuses = [s[0] for s in ProductionJob.Status.choices]
    if new_status not in valid_statuses:
        return JsonResponse({'error': 'Invalid status'}, status=400)

    job.status = new_status
    if new_status == 'in_progress' and not job.start_date:
        job.start_date = timezone.now()
    if new_status == 'completed':
        job.end_date = timezone.now()
    job.save()

    return JsonResponse({'success': True, 'status': new_status, 'status_display': job.get_status_display()})


@app_permission_required('production_edit')
def assign_job(request, pk):
    job = get_object_or_404(ProductionJob, pk=pk)
    if request.method == 'POST':
        from apps.employees.models import Employee
        employee_id = request.POST.get('employee_id')
        if employee_id:
            employee = get_object_or_404(Employee, pk=employee_id)
            job.assigned_to = employee
            job.save()
            messages.success(request, f'تم إسناد المهمة إلى {employee}')
        else:
            messages.error(request, 'الرجاء اختيار موظف')
        return redirect('production:production_job_detail', pk=job.pk)

    from apps.employees.models import Employee
    employees = Employee.objects.filter(is_active=True)
    context = {'job': job, 'employees': employees, 'title': 'إسناد مهمة'}
    return render(request, 'production/assign_job.html', context)


@app_permission_required('production_quality')
def quality_check_create(request, job_pk):
    job = get_object_or_404(ProductionJob, pk=job_pk)
    if request.method == 'POST':
        form = QualityCheckForm(request.POST, request.FILES)
        if form.is_valid():
            check = form.save(commit=False)
            check.production_job = job
            check.save()
            if check.result == 'passed':
                job.status = 'completed'
            elif check.result == 'failed':
                job.status = 'rejected'
            else:
                job.status = 'quality_check'
            job.save()
            messages.success(request, 'تم إضافة فحص الجودة بنجاح')
            return redirect('production:production_job_detail', pk=job.pk)
    else:
        form = QualityCheckForm(initial={'production_job': job})

    context = {'form': form, 'job': job, 'title': 'فحص جودة'}
    return render(request, 'production/production_job_form.html', context)


@app_permission_required('production_view')
def machine_list(request):
    machines = Machine.objects.select_related('department').all()
    department_id = request.GET.get('department')
    machine_type = request.GET.get('machine_type')

    if department_id:
        machines = machines.filter(department_id=department_id)
    if machine_type:
        machines = machines.filter(machine_type=machine_type)

    departments = Department.objects.all()
    context = {
        'machines': machines,
        'departments': departments,
        'title': 'الماكينات',
    }
    return render(request, 'production/machine_list.html', context)


@app_permission_required('production_create')
def machine_create(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الماكينة بنجاح')
            return redirect('production:machine_list')
    else:
        form = MachineForm()

    context = {'form': form, 'title': 'إضافة ماكينة'}
    return render(request, 'production/production_job_form.html', context)


@app_permission_required('production_edit')
def machine_edit(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if request.method == 'POST':
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الماكينة بنجاح')
            return redirect('production:machine_list')
    else:
        form = MachineForm(instance=machine)

    context = {'form': form, 'title': 'تعديل ماكينة'}
    return render(request, 'production/production_job_form.html', context)


@app_permission_required('production_view')
def department_list(request):
    departments = Department.objects.all()
    context = {
        'departments': departments,
        'title': 'أقسام الإنتاج',
    }
    return render(request, 'production/department_list.html', context)


@app_permission_required('production_view')
def production_report(request):
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    department_id = request.GET.get('department')

    jobs = ProductionJob.objects.all()

    if date_from:
        jobs = jobs.filter(created_at__date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        jobs = jobs.filter(created_at__date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())
    if department_id:
        jobs = jobs.filter(department_id=department_id)

    completed = jobs.filter(status='completed')
    rejected = jobs.filter(status='rejected')

    total_jobs = jobs.count()
    completed_count = completed.count()
    rejected_count = rejected.count()

    efficiency_data = jobs.filter(actual_hours__isnull=False).aggregate(
        avg_actual_hours=Avg('actual_hours'),
        total_actual_hours=Sum('actual_hours'),
    )

    departments = Department.objects.all()
    context = {
        'total_jobs': total_jobs,
        'completed_count': completed_count,
        'rejected_count': rejected_count,
        'completion_rate': (completed_count / total_jobs * 100) if total_jobs else 0,
        'efficiency_data': efficiency_data,
        'departments': departments,
        'title': 'تقرير الإنتاج',
    }
    return render(request, 'production/production_dashboard.html', context)


@app_permission_required('production_create')
def quick_add_department(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        name_ar = request.POST.get('name_ar', '').strip()
        code = request.POST.get('code', '').strip()
        if not name or not code:
            return JsonResponse({'success': False, 'error': 'Name and Code required'})
        dept = Department.objects.create(name=name, name_ar=name_ar or name, code=code)
        return JsonResponse({'success': True, 'id': dept.pk, 'text': str(dept)})
    return JsonResponse({'success': False, 'error': 'POST required'})


@app_permission_required('production_create')
def quick_add_machine(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        machine_type = request.POST.get('machine_type', '')
        department_id = request.POST.get('department')
        if not name or not department_id:
            return JsonResponse({'success': False, 'error': 'Name and Department required'})
        machine = Machine.objects.create(
            name=name, machine_type=machine_type or 'other',
            department_id=department_id, status='active'
        )
        return JsonResponse({'success': True, 'id': machine.pk, 'text': str(machine)})
    return JsonResponse({'success': False, 'error': 'POST required'})


@app_permission_required('production_view')
def quick_add_employee(request):
    if request.method == 'POST':
        from apps.employees.models import Employee
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        position = request.POST.get('position', '').strip()
        department = request.POST.get('department', '').strip()
        if not full_name:
            return JsonResponse({'success': False, 'error': 'Name required'})
        emp = Employee.objects.create(
            full_name=full_name, phone=phone, position=position or 'موظف',
            department=department or 'production',
            hire_date=timezone.now().date(), base_salary=0, salary_type='fixed'
        )
        return JsonResponse({'success': True, 'id': emp.pk, 'text': str(emp)})
    return JsonResponse({'success': False, 'error': 'POST required'})
