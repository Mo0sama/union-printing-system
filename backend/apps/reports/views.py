from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import app_permission_required
from django.db.models import Sum, Count, Avg, Q, Value, DecimalField, F, CharField
from django.db.models.functions import Coalesce, TruncDay, TruncMonth, TruncYear
from django.utils import timezone
from datetime import date, timedelta, datetime
from decimal import Decimal

from .forms import DateRangeForm, ReportFilterForm


@app_permission_required('reports_view')
def report_dashboard(request):
    context = {
        'title': 'التقارير',
    }
    return render(request, 'reports/report_dashboard.html', context)


@app_permission_required('reports_view')
def sales_report(request):
    form = ReportFilterForm(request.GET or None)
    sales_qs = _get_sales_queryset(form)

    period = request.GET.get('group_by', 'month')
    if period == 'day':
        trunc_fn = TruncDay('sale_date')
    elif period == 'year':
        trunc_fn = TruncYear('sale_date')
    else:
        trunc_fn = TruncMonth('sale_date')

    sales_by_period = sales_qs.annotate(
        period=trunc_fn
    ).values('period').annotate(
        count=Count('id'),
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField()),
        subtotal=Coalesce(Sum('subtotal'), Value(0), output_field=DecimalField()),
        discount=Coalesce(Sum('discount'), Value(0), output_field=DecimalField()),
        tax=Coalesce(Sum('tax'), Value(0), output_field=DecimalField()),
    ).order_by('period')

    summary = sales_qs.aggregate(
        total_sales=Coalesce(Sum('total'), Value(0), output_field=DecimalField()),
        total_count=Count('id'),
        avg_sale=Avg('total'),
        total_discount=Coalesce(Sum('discount'), Value(0), output_field=DecimalField()),
        total_tax=Coalesce(Sum('tax'), Value(0), output_field=DecimalField()),
    )

    by_payment = sales_qs.values('payment_method').annotate(
        count=Count('id'),
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField()),
    )

    from apps.pos.models import PAYMENT_METHOD_CHOICES
    payment_labels = dict(PAYMENT_METHOD_CHOICES)

    context = {
        'form': form,
        'sales_by_period': sales_by_period,
        'summary': summary,
        'by_payment': by_payment,
        'payment_labels': payment_labels,
        'title': 'تقرير المبيعات',
    }
    return render(request, 'reports/sales_report.html', context)


@app_permission_required('reports_view')
def revenue_report(request):
    form = DateRangeForm(request.GET or None)
    from apps.pos.models import POSSale
    from apps.orders.models import Order, OrderPayment

    sales_qs = POSSale.objects.filter(status='completed')
    payment_qs = OrderPayment.objects.all()

    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')
        if start:
            sales_qs = sales_qs.filter(sale_date__date__gte=start)
            payment_qs = payment_qs.filter(payment_date__gte=start)
        if end:
            sales_qs = sales_qs.filter(sale_date__date__lte=end)
            payment_qs = payment_qs.filter(payment_date__lte=end)

    period = request.GET.get('group_by', 'month')

    from django.db.models.functions import TruncDay as TD, TruncMonth as TM, TruncYear as TY

    if period == 'day':
        trunc_fn = TD('sale_date')
    elif period == 'year':
        trunc_fn = TY('sale_date')
    else:
        trunc_fn = TM('sale_date')

    revenue_by_period = sales_qs.annotate(
        period=trunc_fn
    ).values('period').annotate(
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField()),
        count=Count('id'),
    ).order_by('period')

    order_revenue = payment_qs.aggregate(
        total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
    )['total']

    by_payment = sales_qs.values('payment_method').annotate(
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField()),
        count=Count('id'),
    )

    total_pos_revenue = sales_qs.aggregate(
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField())
    )['total']
    total_revenue = total_pos_revenue + order_revenue

    from apps.pos.models import PAYMENT_METHOD_CHOICES
    payment_labels = dict(PAYMENT_METHOD_CHOICES)

    context = {
        'form': form,
        'revenue_by_period': revenue_by_period,
        'by_payment': by_payment,
        'total_revenue': total_revenue,
        'order_revenue': order_revenue,
        'payment_labels': payment_labels,
        'title': 'تقرير الإيرادات',
    }
    return render(request, 'reports/revenue_report.html', context)


@app_permission_required('reports_view')
def expenses_report(request):
    form = DateRangeForm(request.GET or None)
    from apps.orders.models import Order  # Assuming Orders track costs

    start = end = None
    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')

    expenses_data = []

    salary_costs = 0
    adv_total = 0
    from apps.employees.models import EmployeeSalary, EmployeeAdvance
    salary_qs = EmployeeSalary.objects.all()
    adv_qs = EmployeeAdvance.objects.all()
    if start:
        salary_qs = salary_qs.filter(
            Q(payment_date__gte=start) | Q(created_at__date__gte=start)
        )
        adv_qs = adv_qs.filter(date__gte=start)
    if end:
        salary_qs = salary_qs.filter(
            Q(payment_date__lte=end) | Q(created_at__date__lte=end)
        )
        adv_qs = adv_qs.filter(date__lte=end)

    salary_costs = salary_qs.aggregate(
        total=Coalesce(Sum('net_salary'), Value(0), output_field=DecimalField())
    )['total']

    adv_total = adv_qs.aggregate(
        total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
    )['total']

    expenses_data = [
        {'category': 'الرواتب', 'amount': salary_costs, 'count': salary_qs.count()},
        {'category': 'السلف', 'amount': adv_total, 'count': adv_qs.count()},
    ]

    total_expenses = salary_costs + adv_total

    context = {
        'form': form,
        'expenses_data': expenses_data,
        'total_expenses': total_expenses,
        'title': 'تقرير المصروفات',
    }
    return render(request, 'reports/expenses_report.html', context)


@app_permission_required('reports_view')
def profit_loss_report(request):
    form = DateRangeForm(request.GET or None)
    from apps.pos.models import POSSale

    income_qs = POSSale.objects.filter(status='completed')
    start = end = None
    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')
        if start:
            income_qs = income_qs.filter(sale_date__date__gte=start)
        if end:
            income_qs = income_qs.filter(sale_date__date__lte=end)

    total_income = income_qs.aggregate(
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField())
    )['total']

    from apps.employees.models import EmployeeSalary
    salary_qs = EmployeeSalary.objects.all()
    if start:
        salary_qs = salary_qs.filter(created_at__date__gte=start)
    if end:
        salary_qs = salary_qs.filter(created_at__date__lte=end)

    salary_costs = salary_qs.aggregate(
        total=Coalesce(Sum('net_salary'), Value(0), output_field=DecimalField())
    )['total']

    total_expenses = salary_costs
    net_profit = total_income - total_expenses

    context = {
        'form': form,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'profit_margin': (net_profit / total_income * 100) if total_income else 0,
        'title': 'تقرير الأرباح والخسائر',
    }
    return render(request, 'reports/profit_loss_report.html', context)


@app_permission_required('reports_view')
def customer_report(request):
    form = DateRangeForm(request.GET or None)
    from apps.pos.models import POSSale
    from apps.customers.models import Customer

    sales_qs = POSSale.objects.filter(status='completed')
    start = end = None
    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')
        if start:
            sales_qs = sales_qs.filter(sale_date__date__gte=start)
        if end:
            sales_qs = sales_qs.filter(sale_date__date__lte=end)

    top_customers = sales_qs.values(
        'customer__id', 'customer__name', 'customer__company_name', 'customer__phone'
    ).annotate(
        total_spent=Coalesce(Sum('total'), Value(0), output_field=DecimalField()),
        order_count=Count('id'),
    ).order_by('-total_spent')[:20]

    total_customers = Customer.objects.count()

    new_customers = Customer.objects.all()
    if start:
        new_customers = new_customers.filter(created_at__date__gte=start)
    if end:
        new_customers = new_customers.filter(created_at__date__lte=end)

    context = {
        'form': form,
        'top_customers': top_customers,
        'total_customers': total_customers,
        'new_customers_count': new_customers.count(),
        'title': 'تقرير العملاء',
    }
    return render(request, 'reports/customer_report.html', context)


@app_permission_required('reports_view')
def production_report(request):
    from apps.production.models import ProductionJob

    jobs = ProductionJob.objects.all()

    status_counts = jobs.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    total_jobs = jobs.count()
    completed_count = jobs.filter(status='completed').count()

    context = {
        'status_counts': status_counts,
        'total_jobs': total_jobs,
        'completed_count': completed_count,
        'title': 'تقرير الإنتاج',
    }
    return render(request, 'reports/production_report.html', context)


@app_permission_required('reports_view')
def inventory_report(request):
    from apps.inventory.models import Material, StockMovement

    materials = Material.objects.all()
    total_items = materials.count()
    total_value = materials.aggregate(
        total=Coalesce(
            Sum(F('current_stock') * F('purchase_price')),
            Value(0), output_field=DecimalField()
        )
    )['total']

    low_stock = materials.filter(current_stock__lte=F('minimum_stock'))
    out_of_stock = materials.filter(current_stock__lte=0)

    movements = StockMovement.objects.all().order_by('-created_at')[:50]

    context = {
        'total_items': total_items,
        'total_value': total_value,
        'low_stock_count': low_stock.count(),
        'low_stock_products': low_stock,
        'out_of_stock_count': out_of_stock.count(),
        'movements': movements,
        'title': 'تقرير المخزون',
    }
    return render(request, 'reports/inventory_report.html', context)


@app_permission_required('reports_view')
def employee_report(request):
    from apps.employees.models import Employee, Attendance, EmployeeSalary, EmployeeLeave

    department = request.GET.get('department', '')

    employees = Employee.objects.all()
    if department:
        employees = employees.filter(department=department)

    total_employees = employees.count()
    active_employees = employees.filter(is_active=True).count()

    salary_cost = EmployeeSalary.objects.filter(
        paid=True
    ).aggregate(
        total=Coalesce(Sum('net_salary'), Value(0), output_field=DecimalField())
    )['total']

    dept_stats = employees.values('department').annotate(
        count=Count('id'),
        total_salary=Coalesce(Sum('base_salary'), Value(0), output_field=DecimalField()),
    )

    from apps.employees.models import DEPARTMENT_CHOICES
    context = {
        'employees': employees,
        'total_employees': total_employees,
        'active_employees': active_employees,
        'salary_cost': salary_cost,
        'dept_stats': dept_stats,
        'department': department,
        'departments': DEPARTMENT_CHOICES,
        'title': 'تقرير الموظفين',
    }
    return render(request, 'reports/employee_report.html', context)


@app_permission_required('reports_view')
def tax_report(request):
    form = DateRangeForm(request.GET or None)
    from apps.pos.models import POSSale

    sales_qs = POSSale.objects.filter(status='completed')
    start = end = None
    if form.is_valid():
        start = form.cleaned_data.get('start_date')
        end = form.cleaned_data.get('end_date')
        if start:
            sales_qs = sales_qs.filter(sale_date__date__gte=start)
        if end:
            sales_qs = sales_qs.filter(sale_date__date__lte=end)

    tax_summary_by_period = sales_qs.annotate(
        period=TruncMonth('sale_date')
    ).values('period').annotate(
        total_sales=Coalesce(Sum('total'), Value(0), output_field=DecimalField()),
        total_tax=Coalesce(Sum('tax'), Value(0), output_field=DecimalField()),
        count=Count('id'),
    ).order_by('period')

    summary = sales_qs.aggregate(
        total_sales=Coalesce(Sum('total'), Value(0), output_field=DecimalField()),
        total_tax=Coalesce(Sum('tax'), Value(0), output_field=DecimalField()),
        count=Count('id'),
    )

    context = {
        'form': form,
        'tax_summary_by_period': tax_summary_by_period,
        'summary': summary,
        'title': 'تقرير الضرائب',
    }
    return render(request, 'reports/tax_report.html', context)


def _export_sales(ws):
    from apps.pos.models import POSSale
    ws.append(['رقم الفاتورة', 'التاريخ', 'الإجمالي', 'طريقة الدفع', 'الحالة'])
    for sale in POSSale.objects.all()[:1000]:
        ws.append([sale.sale_number, sale.sale_date.strftime('%Y-%m-%d %H:%M'),
                   float(sale.total), sale.get_payment_method_display(), sale.get_status_display()])


def _export_revenue(ws):
    from apps.orders.models import OrderPayment
    ws.append(['التاريخ', 'الطلب', 'المبلغ', 'طريقة الدفع'])
    for p in OrderPayment.objects.all()[:1000]:
        ws.append([p.payment_date.strftime('%Y-%m-%d'), str(p.order.order_number),
                   float(p.amount), p.get_payment_method_display()])


def _export_profit_loss(ws):
    from apps.orders.models import Order
    ws.append(['رقم الطلب', 'العميل', 'التاريخ', 'الإجمالي', 'المدفوع', 'المتبقي'])
    for o in Order.objects.all()[:500]:
        ws.append([o.order_number, str(o.customer), o.created_at.strftime('%Y-%m-%d'),
                   float(o.total), float(o.paid_amount), float(o.due_amount)])


def _export_customers(ws):
    from apps.customers.models import Customer
    ws.append(['الكود', 'الاسم', 'الهاتف', 'الرصيد', 'الحد الائتماني', 'تاريخ التسجيل'])
    for c in Customer.objects.all()[:500]:
        ws.append([c.code, str(c), c.phone, float(c.current_balance),
                   float(c.credit_limit), c.created_at.strftime('%Y-%m-%d')])


def _export_production(ws):
    from apps.production.models import ProductionJob
    ws.append(['رقم الأمر', 'الطلب', 'القسم', 'الحالة', 'تاريخ البدء', 'تاريخ الانتهاء'])
    for j in ProductionJob.objects.all()[:500]:
        ws.append([j.job_number, j.order.order_number, j.department.name_ar,
                   j.get_status_display(),
                   j.start_date.strftime('%Y-%m-%d %H:%M') if j.start_date else '',
                   j.end_date.strftime('%Y-%m-%d %H:%M') if j.end_date else ''])


def _export_inventory(ws):
    from apps.inventory.models import Material
    ws.append(['الكود', 'الاسم', 'التصنيف', 'الوحدة', 'المخزون', 'سعر الشراء', 'سعر البيع'])
    for m in Material.objects.all()[:500]:
        ws.append([m.code, m.name_ar or m.name, m.category.name_ar if m.category else '',
                   m.get_unit_display(), float(m.current_stock),
                   float(m.purchase_price), float(m.selling_price or 0)])


def _export_employees(ws):
    from apps.employees.models import Employee
    ws.append(['الكود', 'الاسم', 'القسم', 'الراتب', 'الحالة'])
    for emp in Employee.objects.all():
        ws.append([emp.employee_code, emp.full_name, emp.get_department_display(),
                   float(emp.base_salary), 'نشط' if emp.is_active else 'غير نشط'])


def _export_tax(ws):
    from apps.orders.models import Order
    ws.append(['رقم الطلب', 'العميل', 'التاريخ', 'الإجمالي', 'الضريبة', 'نسبة الضريبة'])
    for o in Order.objects.filter(tax_amount__gt=0)[:500]:
        ws.append([o.order_number, str(o.customer), o.created_at.strftime('%Y-%m-%d'),
                   float(o.total), float(o.tax_amount), f'{o.tax_percentage}%'])


EXPORT_HANDLERS = {
    'sales': _export_sales,
    'revenue': _export_revenue,
    'profit_loss': _export_profit_loss,
    'customers': _export_customers,
    'production': _export_production,
    'inventory': _export_inventory,
    'employees': _export_employees,
    'tax': _export_tax,
}


@app_permission_required('reports_view')
def export_report_excel(request):
    import openpyxl
    from django.http import HttpResponse

    report_type = request.GET.get('type', 'sales')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'التقرير'

    handler = EXPORT_HANDLERS.get(report_type)
    if handler:
        handler(ws)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
    wb.save(response)
    return response


@app_permission_required('reports_view')
def print_report(request):
    report_type = request.GET.get('type', 'sales')
    template_map = {
        'sales': 'reports/sales_report.html',
        'revenue': 'reports/revenue_report.html',
        'profit_loss': 'reports/profit_loss_report.html',
        'employees': 'reports/employee_report.html',
    }
    template = template_map.get(report_type, 'reports/sales_report.html')
    context = {'print_mode': True}
    return render(request, template, context)


def _get_sales_queryset(form):
    from apps.pos.models import POSSale
    qs = POSSale.objects.filter(status='completed')

    if form.is_valid() and hasattr(form, 'cleaned_data'):
        cd = form.cleaned_data
        if cd.get('date_from'):
            qs = qs.filter(sale_date__date__gte=cd['date_from'])
        if cd.get('date_to'):
            qs = qs.filter(sale_date__date__lte=cd['date_to'])
        if cd.get('status'):
            qs = qs.filter(status=cd['status'])
    return qs
