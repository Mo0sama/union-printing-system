from datetime import datetime

from django import forms
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from apps.accounts.decorators import app_permission_required
from django.db.models import Count, F, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import ActivityLog, CompanySetting


class CompanySettingForm(forms.ModelForm):
    class Meta:
        model = CompanySetting
        exclude = ('pk',)
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'logo': forms.FileInput(),
        }


@app_permission_required('dashboard_view')
def dashboard(request):
    today = timezone.now().date()

    today_orders = 0
    pending_production = 0
    monthly_revenue = 0
    total_customers = 0
    recent_orders = []
    production_jobs = []
    low_stock_items = []

    try:
        from apps.orders.models import Order, OrderPayment
        today_orders = Order.objects.filter(created_at__date=today).count()
        monthly_revenue = OrderPayment.objects.filter(
            payment_date__month=today.month,
            payment_date__year=today.year,
        ).aggregate(total=Sum('amount'))['total'] or 0
        recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:10]
    except Exception:
        pass

    try:
        from apps.production.models import ProductionJob
        pending_production = ProductionJob.objects.filter(
            status__in=['pending', 'in_progress']
        ).count()
        production_jobs = ProductionJob.objects.select_related('order').order_by('-created_at')[:5]
    except Exception:
        pass

    try:
        from apps.customers.models import Customer
        total_customers = Customer.objects.filter(is_active=True).count()
    except Exception:
        pass

    try:
        from apps.inventory.models import Material
        low_stock_items = Material.objects.filter(
            current_stock__lte=F('minimum_stock'),
            is_active=True
        )[:10]
    except Exception:
        pass

    context = {
        'today_orders': today_orders,
        'pending_production': pending_production,
        'monthly_revenue': monthly_revenue,
        'total_customers': total_customers,
        'recent_orders': recent_orders,
        'production_jobs': production_jobs,
        'low_stock_items': low_stock_items,
        'recent_activities': ActivityLog.objects.all()[:10],
    }
    return render(request, 'core/dashboard.html', context)


@app_permission_required('users_view')
def activity_log_list(request):
    logs = ActivityLog.objects.all()
    search = request.GET.get('search', '')
    if search:
        logs = logs.filter(
            Q(user__username__icontains=search) |
            Q(action__icontains=search) |
            Q(model_name__icontains=search) |
            Q(details__icontains=search)
        )
    context = {
        'logs': logs[:100],
        'search': search,
    }
    return render(request, 'core/activity_log.html', context)


@app_permission_required('settings_view')
def settings_view(request):
    settings = CompanySetting.get_settings()
    if request.method == 'POST':
        form = CompanySettingForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully.')
            return redirect('core:settings')
    else:
        form = CompanySettingForm(instance=settings)
    context = {
        'form': form,
        'settings': settings,
    }
    return render(request, 'core/settings.html', context)


@app_permission_required('advanced_settings_view')
def advanced_settings(request):
    from apps.inventory.models import Category
    from apps.production.models import Department, Machine
    from .models import Lookup

    categories = Category.objects.all()
    departments = Department.objects.all()
    machines = Machine.objects.select_related('department').all()

    lookup_sections = {}
    for lt in Lookup.Type.values:
        lookup_sections[lt] = Lookup.objects.filter(type=lt, is_active=True)

    model_sections = ['category', 'department', 'machine']
    lookup_type_map = {lt: lt for lt in Lookup.Type.values}

    if request.method == 'POST':
        item_type = request.POST.get('type')
        action = request.POST.get('action')
        pk = request.POST.get('pk')

        try:
            # Handle model-based sections
            if item_type == 'category':
                if action == 'add':
                    name_ar = request.POST.get('name_ar', '').strip()
                    if name_ar:
                        Category.objects.create(
                            name=request.POST.get('name', name_ar),
                            name_ar=name_ar,
                            parent_id=request.POST.get('parent') or None,
                            description=request.POST.get('description', ''),
                        )
                        messages.success(request, 'تمت إضافة التصنيف بنجاح')
                    else:
                        messages.error(request, 'الاسم بالعربية مطلوب')
                elif action == 'edit' and pk:
                    cat = get_object_or_404(Category, pk=pk)
                    name_ar = request.POST.get('name_ar', '').strip()
                    if name_ar:
                        cat.name = request.POST.get('name', name_ar)
                        cat.name_ar = name_ar
                        cat.parent_id = request.POST.get('parent') or None
                        cat.description = request.POST.get('description', '')
                        cat.save()
                        messages.success(request, 'تم تحديث التصنيف بنجاح')
                    else:
                        messages.error(request, 'الاسم بالعربية مطلوب')
                elif action == 'delete' and pk:
                    Category.objects.filter(pk=pk).delete()
                    messages.success(request, 'تم حذف التصنيف بنجاح')

            elif item_type == 'department':
                if action == 'add':
                    name_ar = request.POST.get('name_ar', '').strip()
                    code = request.POST.get('code', '').strip()
                    if name_ar and code:
                        Department.objects.create(
                            name=request.POST.get('name', name_ar),
                            name_ar=name_ar,
                            code=code,
                            sort_order=int(request.POST.get('sort_order', 0)),
                            description=request.POST.get('description', ''),
                        )
                        messages.success(request, 'تمت إضافة القسم بنجاح')
                    else:
                        messages.error(request, 'الاسم والكود مطلوبان')
                elif action == 'edit' and pk:
                    dept = get_object_or_404(Department, pk=pk)
                    name_ar = request.POST.get('name_ar', '').strip()
                    code = request.POST.get('code', '').strip()
                    if name_ar and code:
                        dept.name = request.POST.get('name', name_ar)
                        dept.name_ar = name_ar
                        dept.code = code
                        dept.sort_order = int(request.POST.get('sort_order', 0))
                        dept.description = request.POST.get('description', '')
                        dept.save()
                        messages.success(request, 'تم تحديث القسم بنجاح')
                    else:
                        messages.error(request, 'الاسم والكود مطلوبان')
                elif action == 'delete' and pk:
                    Department.objects.filter(pk=pk).delete()
                    messages.success(request, 'تم حذف القسم بنجاح')

            elif item_type == 'machine':
                if action == 'delete' and pk:
                    Machine.objects.filter(pk=pk).delete()
                    messages.success(request, 'تم حذف الماكينة بنجاح')
                elif action in ('add', 'edit'):
                    name = request.POST.get('name', '').strip()
                    dept_id = request.POST.get('department')
                    if name and dept_id:
                        if action == 'add':
                            Machine.objects.create(
                                name=name,
                                machine_type=request.POST.get('machine_type', 'other'),
                                department_id=dept_id,
                                model=request.POST.get('model', ''),
                                status=request.POST.get('status', 'active'),
                                notes=request.POST.get('notes', ''),
                            )
                            messages.success(request, 'تمت إضافة الماكينة بنجاح')
                        elif action == 'edit' and pk:
                            mach = get_object_or_404(Machine, pk=pk)
                            mach.name = name
                            mach.machine_type = request.POST.get('machine_type', 'other')
                            mach.department_id = dept_id
                            mach.model = request.POST.get('model', '')
                            mach.status = request.POST.get('status', 'active')
                            mach.notes = request.POST.get('notes', '')
                            mach.save()
                            messages.success(request, 'تم تحديث الماكينة بنجاح')
                    else:
                        messages.error(request, 'الاسم والقسم مطلوبان')

            # Handle Lookup-based sections (material_unit, payment_method, etc.)
            elif item_type in lookup_type_map:
                if action == 'delete' and pk:
                    Lookup.objects.filter(pk=pk).delete()
                    messages.success(request, 'تم الحذف بنجاح')
                elif action in ('add', 'edit'):
                    name_ar = request.POST.get('name_ar', '').strip()
                    code = request.POST.get('code', '').strip()
                    if name_ar and code:
                        if action == 'add':
                            Lookup.objects.create(
                                type=item_type,
                                code=code,
                                name=request.POST.get('name', name_ar),
                                name_ar=name_ar,
                                sort_order=int(request.POST.get('sort_order', 0)),
                            )
                            messages.success(request, 'تمت الإضافة بنجاح')
                        elif action == 'edit' and pk:
                            item = get_object_or_404(Lookup, pk=pk)
                            item.code = code
                            item.name = request.POST.get('name', name_ar)
                            item.name_ar = name_ar
                            item.sort_order = int(request.POST.get('sort_order', 0))
                            item.save()
                            messages.success(request, 'تم التحديث بنجاح')
                    else:
                        messages.error(request, 'الاسم والكود مطلوبان')

        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')

        return redirect('core:advanced_settings')

    # Build structured context for template
    sections = []
    sections.append(('category', 'التصنيفات', 'categories', categories))
    sections.append(('department', 'أقسام الإنتاج', 'departments', departments))
    sections.append(('machine', 'الماكينات', 'machines', machines))

    lookup_labels = {
        'material_unit': 'وحدات القياس', 'payment_method': 'أنواع الدفع',
        'order_type': 'أنواع الطلبات', 'machine_type': 'أنواع الماكينات',
        'employee_dept': 'أقسام الموظفين', 'supplier_type': 'أنواع الموردين',
        'customer_type': 'أنواع العملاء', 'vat': 'الضرائب',
        'order_status': 'حالات الطلبات', 'order_priority': 'أولويات الطلبات',
        'order_item_type': 'أنواع بنود الطلب', 'order_item_status': 'حالات بنود الطلب',
        'unit': 'وحدات القياس', 'discount_type': 'أنواع الخصم',
        'delivery_note_status': 'حالات مذكرات التسليم',
        'production_job_status': 'حالات أوامر الإنتاج',
        'production_stage_status': 'حالات مراحل الإنتاج',
        'quality_check_result': 'نتائج فحص الجودة', 'machine_status': 'حالات الماكينات',
        'quote_status': 'حالات عروض الأسعار', 'stock_movement_type': 'أنواع الحركات المخزنية',
        'pos_session_status': 'حالات جلسات البيع', 'pos_sale_status': 'حالات فواتير البيع',
        'pos_item_type': 'أنواع بنود الفواتير',
        'purchase_order_status': 'حالات أوامر الشراء',
        'interaction_type': 'أنواع التفاعلات', 'customer_payment_method': 'طرق دفع العملاء',
        'leave_type': 'أنواع الإجازات', 'leave_status': 'حالات الإجازات',
        'attendance_status': 'حالات الحضور', 'employee_salary_type': 'أنواع الرواتب',
    }

    lookup_types = [
        'material_unit', 'payment_method', 'order_type', 'machine_type',
        'employee_dept', 'supplier_type', 'customer_type', 'vat',
        'order_status', 'order_priority', 'order_item_type', 'order_item_status',
        'unit', 'discount_type', 'delivery_note_status',
        'production_job_status', 'production_stage_status', 'quality_check_result',
        'machine_status', 'quote_status', 'stock_movement_type',
        'pos_session_status', 'pos_sale_status', 'pos_item_type',
        'purchase_order_status', 'interaction_type', 'customer_payment_method',
        'leave_type', 'leave_status', 'attendance_status', 'employee_salary_type',
    ]

    context = {
        'categories': categories,
        'departments': departments,
        'machines': machines,
        'lookup_sections': lookup_sections,
        'lookup_labels': lookup_labels,
        'lookup_types': lookup_types,
    }
    return render(request, 'core/advanced_settings.html', context)


@require_POST
@app_permission_required('settings_view')
def clear_notifications(request):
    messages.success(request, 'Notifications cleared.')
    return redirect('core:dashboard')
