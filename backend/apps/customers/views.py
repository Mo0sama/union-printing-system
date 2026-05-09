import openpyxl
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.accounts.decorators import app_permission_required
from apps.core.validators import sanitize_excel_value
from apps.orders.models import Order, OrderPayment

from .forms import (
    CustomerForm,
    CustomerInteractionForm,
    CustomerPaymentForm,
)
from .models import Customer, CustomerPayment
from .services import record_customer_payment


@app_permission_required('customers_view')
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')

    search = request.GET.get('search', '')
    customer_type = request.GET.get('type', '')
    status = request.GET.get('status', '')

    if search:
        customers = customers.filter(
            Q(code__icontains=search) |
            Q(name__icontains=search) |
            Q(company_name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )
    if customer_type:
        customers = customers.filter(customer_type=customer_type)
    if status == 'active':
        customers = customers.filter(is_active=True)
    elif status == 'inactive':
        customers = customers.filter(is_active=False)

    paginator = Paginator(customers, 25)
    page = request.GET.get('page', 1)
    customers_page = paginator.get_page(page)

    context = {
        'customers': customers_page,
        'search': search,
        'customer_type': customer_type,
        'status': status,
    }
    return render(request, 'customers/customer_list.html', context)


@app_permission_required('customers_view')
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    interactions = customer.interactions.all()[:20]

    orders = Order.objects.filter(customer=customer).prefetch_related('payments').order_by('-created_at')
    order_payments = OrderPayment.objects.filter(order__customer=customer).select_related('order').order_by('-payment_date')[:50]
    customer_payments = CustomerPayment.objects.filter(customer=customer)[:20]

    total_order_amount = sum(o.total for o in orders if o.status != 'cancelled')
    total_paid = sum(p.amount for p in order_payments)

    context = {
        'customer': customer,
        'interactions': interactions,
        'orders': orders,
        'order_payments': order_payments,
        'customer_payments': customer_payments,
        'total_order_amount': total_order_amount,
        'total_paid': total_paid,
    }
    return render(request, 'customers/customer_detail.html', context)


@app_permission_required('customers_create')
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.created_by = request.user
            customer.save()
            messages.success(request, _('تم إنشاء العميل بنجاح.'))
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm()

    return render(request, 'customers/customer_form.html', {
        'form': form,
        'title': _('إضافة عميل جديد'),
    })


@app_permission_required('customers_create')
def quick_add_customer(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'الاسم مطلوب'})
        if not phone:
            return JsonResponse({'success': False, 'error': 'رقم الهاتف مطلوب'})
        customer = Customer.objects.create(
            customer_type=Customer.CustomerType.INDIVIDUAL,
            name=name,
            phone=phone,
            created_by=request.user,
        )
        return JsonResponse({
            'success': True, 'id': customer.pk, 'text': str(customer)
        })
    return JsonResponse({'success': False, 'error': 'POST required'})


@app_permission_required('customers_edit')
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث بيانات العميل بنجاح.'))
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customers/customer_form.html', {
        'form': form,
        'title': _('تعديل بيانات العميل'),
        'customer': customer,
    })


@app_permission_required('customers_delete')
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        name = str(customer)
        customer.delete()
        messages.success(request, _('تم حذف العميل "%s" بنجاح.') % name)
        return redirect('customers:customer_list')

    return render(request, 'customers/customer_confirm_delete.html', {
        'customer': customer,
    })


@app_permission_required('customers_edit')
def add_interaction(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerInteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.customer = customer
            interaction.created_by = request.user
            interaction.save()
            messages.success(request, _('تم تسجيل التفاعل بنجاح.'))
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerInteractionForm()

    return render(request, 'customers/interaction_form.html', {
        'form': form,
        'customer': customer,
        'title': _('إضافة تفاعل جديد'),
    })


@app_permission_required('customers_edit')
def add_payment(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST)
        if form.is_valid():
            record_customer_payment(
                customer=customer,
                amount=form.cleaned_data['amount'],
                payment_date=form.cleaned_data.get('payment_date'),
                payment_method=form.cleaned_data.get('payment_method', 'cash'),
                reference=form.cleaned_data.get('reference', ''),
                notes=form.cleaned_data.get('notes', ''),
                user=request.user,
            )
            messages.success(request, _('تم تسجيل الدفعة بنجاح.'))
            return redirect('customers:customer_detail', pk=customer.pk)
    else:
        form = CustomerPaymentForm(initial={'payment_date': None})

    return render(request, 'customers/payment_form.html', {
        'form': form,
        'customer': customer,
        'title': _('تسجيل دفعة جديدة'),
    })


@app_permission_required('customers_view')
def customer_statement(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    interactions = customer.interactions.all().order_by('-created_at')

    orders = Order.objects.filter(customer=customer).prefetch_related('payments').order_by('-created_at')
    order_payments = OrderPayment.objects.filter(order__customer=customer).select_related('order').order_by('-payment_date')
    customer_payments = customer.payments.all().order_by('-payment_date')

    total_order_amount = sum(o.total for o in orders if o.status != 'cancelled')
    total_paid_orders = sum(p.amount for p in order_payments)
    total_paid_direct = sum(p.amount for p in customer_payments)

    context = {
        'customer': customer,
        'orders': orders,
        'order_payments': order_payments,
        'customer_payments': customer_payments,
        'interactions': interactions,
        'total_order_amount': total_order_amount,
        'total_paid_orders': total_paid_orders,
        'total_paid_direct': total_paid_direct,
    }
    return render(request, 'customers/customer_statement.html', context)


@app_permission_required('customers_view')
def customer_export(request):
    customers = Customer.objects.filter(is_active=True).order_by('-created_at')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = str(_('العملاء'))

    headers = [
        str(_('كود العميل')), str(_('النوع')), str(_('الاسم')),
        str(_('اسم الشركة')), str(_('الشخص المسؤول')), str(_('رقم الهاتف')),
        str(_('الهاتف الثانوي')), str(_('البريد الإلكتروني')), str(_('المدينة')),
        str(_('الرصيد الحالي')), str(_('الحد الائتماني')), str(_('الرقم الضريبي')),
        str(_('ملاحظات')),
    ]
    ws.append(headers)

    for customer in customers:
        ws.append([
            sanitize_excel_value(customer.code),
            sanitize_excel_value(customer.get_customer_type_display()),
            sanitize_excel_value(customer.name or customer.contact_person or customer.company_name),
            sanitize_excel_value(customer.company_name),
            sanitize_excel_value(customer.contact_person),
            sanitize_excel_value(customer.phone),
            sanitize_excel_value(customer.secondary_phone),
            sanitize_excel_value(customer.email),
            sanitize_excel_value(customer.city),
            str(customer.current_balance),
            str(customer.credit_limit),
            sanitize_excel_value(customer.tax_number),
            sanitize_excel_value(customer.notes),
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="customers_{__import__("datetime").datetime.now().strftime("%Y%m%d")}.xlsx"'
    wb.save(response)
    return response
