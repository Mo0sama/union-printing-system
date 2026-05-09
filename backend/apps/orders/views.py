from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounting.services import post_cogs, post_order_revenue
from apps.core.models import CompanySetting
from apps.inventory.services import deduct_stock_fifo, reverse_stock_deduction

from .forms import (
    DeliveryNoteForm,
    DesignFileForm,
    OrderFilterForm,
    OrderForm,
    OrderItemFormSet,
    OrderPaymentForm,
)
from .models import DeliveryNote, DesignFile, Order, OrderPayment
from .services import adjust_customer_balance_for_order, adjust_customer_balance_for_payment


@login_required
@permission_required('orders.view_order', raise_exception=True)
def order_list(request):
    queryset = Order.objects.select_related(
        'customer', 'created_by'
    ).prefetch_related('items', 'payments').all()
    filter_form = OrderFilterForm(request.GET)

    if filter_form.is_valid():
        cd = filter_form.cleaned_data
        if cd.get('status'):
            queryset = queryset.filter(status=cd['status'])
        if cd.get('priority'):
            queryset = queryset.filter(priority=cd['priority'])
        if cd.get('payment_status'):
            queryset = queryset.filter(payment_status=cd['payment_status'])
        if cd.get('customer'):
            queryset = queryset.filter(
                customer__name__icontains=cd['customer']
            ) | queryset.filter(
                customer__company_name__icontains=cd['customer']
            ) | queryset.filter(
                customer__contact_person__icontains=cd['customer']
            )
        if cd.get('date_from'):
            queryset = queryset.filter(order_date__date__gte=cd['date_from'])
        if cd.get('date_to'):
            queryset = queryset.filter(order_date__date__lte=cd['date_to'])
        if cd.get('search'):
            queryset = queryset.filter(
                order_number__icontains=cd['search']
            )

    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'title': _('الطلبات'),
    }
    return render(request, 'orders/order_list.html', context)


@login_required
@permission_required('orders.view_order', raise_exception=True)
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related(
            'customer', 'quote', 'created_by'
        ).prefetch_related(
            'items', 'payments', 'design_files', 'delivery_notes'
        ),
        pk=pk
    )
    context = {
        'order': order,
        'payment_form': OrderPaymentForm(initial={'payment_date': timezone.now().date()}),
        'design_file_form': DesignFileForm(),
        'title': _('طلب: %s') % order.order_number,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
@permission_required('orders.add_order', raise_exception=True)
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.created_by = request.user
                    order.save()
                    formset.instance = order
                    formset.save()
                    order.calculate_totals()
                    order.update_payment_status()
                    adjust_customer_balance_for_order(order, order.total)
                messages.success(request, _('تم إنشاء الطلب بنجاح'))
                return redirect('orders:order_detail', pk=order.pk)
            except Exception as e:
                messages.error(request, _('حدث خطأ: %s') % str(e))
        else:
            messages.error(request, _('يرجى تصحيح الأخطاء أدناه'))
    else:
        initial = {'delivery_date': timezone.now().date() + timedelta(days=7)}
        quote_pk = request.GET.get('quote')
        if quote_pk:
            from apps.quotes.models import Quote
            try:
                quote = Quote.objects.prefetch_related('items').get(pk=quote_pk)
                initial.update({
                    'customer': quote.customer,
                    'quote': quote,
                })
            except Quote.DoesNotExist:
                pass
        form = OrderForm(initial=initial)
        formset = OrderItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': _('إنشاء طلب جديد'),
        'is_create': True,
    }
    return render(request, 'orders/order_form.html', context)


@login_required
@permission_required('orders.change_order', raise_exception=True)
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    old_total = Order.objects.get(pk=order.pk).total
                    order = form.save()
                    formset.save()
                    order.calculate_totals()
                    order.update_payment_status()
                    adjust_customer_balance_for_order(order, order.total - old_total)
                messages.success(request, _('تم تحديث الطلب بنجاح'))
                return redirect('orders:order_detail', pk=order.pk)
            except Exception as e:
                messages.error(request, _('حدث خطأ: %s') % str(e))
        else:
            messages.error(request, _('يرجى تصحيح الأخطاء أدناه'))
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    context = {
        'form': form,
        'formset': formset,
        'order': order,
        'title': _('تعديل الطلب: %s') % order.order_number,
        'is_create': False,
    }
    return render(request, 'orders/order_form.html', context)


@login_required
@permission_required('orders.delete_order', raise_exception=True)
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        adjust_customer_balance_for_order(order, -order.total)
        order.delete()
        messages.success(request, _('تم حذف الطلب بنجاح'))
        return redirect('orders:order_list')
    context = {
        'order': order,
        'title': _('حذف الطلب'),
    }
    return render(request, 'orders/order_confirm_delete.html', context)


@login_required
@permission_required('orders.add_orderpayment', raise_exception=True)
def add_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderPaymentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    payment = form.save(commit=False)
                    payment.order = order
                    payment.created_by = request.user
                    if not payment.payment_date:
                        payment.payment_date = timezone.now().date()
                    payment.save()
                    order.update_payment_status()
                    adjust_customer_balance_for_payment(payment)
                messages.success(request, _('تم إضافة الدفعة بنجاح'))
                return redirect('orders:payment_receipt', pk=pk, payment_pk=payment.pk)
            except Exception as e:
                messages.error(request, _('حدث خطأ: %s') % str(e))
        else:
            messages.error(request, _('يرجى تصحيح الأخطاء'))
    return redirect('orders:order_detail', pk=pk)


@login_required
@permission_required('orders.add_designfile', raise_exception=True)
def add_design_file(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        files = request.FILES.getlist('file')
        if not files:
            messages.error(request, _('يرجى اختيار ملف'))
            return redirect('orders:order_detail', pk=pk)
        last_version = order.design_files.order_by('-version').first()
        base_version = (last_version.version + 1) if last_version else 1
        saved = 0
        for i, f in enumerate(files):
            try:
                DesignFile.objects.create(
                    order=order,
                    file=f,
                    version=base_version + i,
                    uploaded_by=request.user,
                    notes=request.POST.get('notes', ''),
                )
                saved += 1
            except Exception as e:
                messages.error(request, _('خطأ في رفع %s: %s') % (f.name, str(e)))
        if saved:
            messages.success(request, _('تم رفع %s ملف(ات) بنجاح') % saved)
    return redirect('orders:order_detail', pk=pk)


@login_required
@permission_required('orders.change_order', raise_exception=True)
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.Status.choices):
            old_status = order.status
            order.status = new_status

            try:
                with transaction.atomic():
                    if new_status in ('confirmed', 'in_production') and old_status == 'pending':
                        for item in order.items.select_related('material').all():
                            if item.material and item.item_type != 'material':
                                continue
                            if item.material:
                                deduct_stock_fifo(
                                    material=item.material,
                                    quantity=item.quantity,
                                    reference_type='order',
                                    reference_id=order.pk,
                                    notes=f'{order.order_number} - {item.description}',
                                    user=request.user,
                                )
                                post_cogs('order', order.pk, user=request.user)
                        if new_status == 'confirmed':
                            post_order_revenue(order, request.user)
                    elif new_status == 'cancelled':
                        reverse_stock_deduction('order', order.pk, user=request.user)
                        adjust_customer_balance_for_order(order, -order.total)

                    order.save()
                messages.success(request, _('تم تحديث حالة الطلب بنجاح'))
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('orders:order_detail', pk=pk)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'new_status': order.get_status_display()})
        else:
            messages.error(request, _('حالة غير صالحة'))
    return redirect('orders:order_detail', pk=pk)


@login_required
@permission_required('orders.add_deliverynote', raise_exception=True)
def delivery_note_create(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = DeliveryNoteForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    note = form.save(commit=False)
                    note.order = order
                    note.save()
                    if note.status == DeliveryNote.DeliveryStatus.FULL:
                        order.status = Order.Status.DELIVERED
                        order.save()
                messages.success(request, _('تم إنشاء مذكرة التسليم بنجاح'))
            except Exception as e:
                messages.error(request, _('حدث خطأ: %s') % str(e))
        else:
            messages.error(request, _('يرجى تصحيح الأخطاء'))
    return redirect('orders:order_detail', pk=pk)


@login_required
@permission_required('orders.view_order', raise_exception=True)
def order_timeline(request, pk):
    order = get_object_or_404(Order, pk=pk)
    from apps.core.models import ActivityLog
    timeline = ActivityLog.objects.filter(
        model_name='Order', object_id=order.pk
    ).select_related('user').order_by('-created_at')

    payments = order.payments.all().select_related('created_by')
    design_files = order.design_files.all().select_related('uploaded_by')
    delivery_notes = order.delivery_notes.all()

    events = []
    for log in timeline:
        events.append({
            'date': log.created_at,
            'type': 'system',
            'user': str(log.user) if log.user else _('النظام'),
            'description': log.details or log.action,
        })
    for payment in payments:
        events.append({
            'date': payment.created_at,
            'type': 'payment',
            'user': str(payment.created_by) if payment.created_by else '',
            'description': _('دفعة: %s - %s') % (payment.amount, payment.get_payment_method_display()),
        })
    for df in design_files:
        events.append({
            'date': df.uploaded_at,
            'type': 'design',
            'user': str(df.uploaded_by) if df.uploaded_by else '',
            'description': _('رفع ملف تصميم (إصدار %s)') % df.version,
        })
    for dn in delivery_notes:
        events.append({
            'date': dn.delivery_date,
            'type': 'delivery',
            'user': dn.delivered_by,
            'description': _('تسليم %s بواسطة %s') % (dn.get_status_display(), dn.delivered_by),
        })

    events.sort(key=lambda x: x['date'], reverse=True)

    context = {
        'order': order,
        'timeline': events,
        'title': _('الخط الزمني للطلب: %s') % order.order_number,
    }
    return render(request, 'orders/order_timeline.html', context)


@login_required
@permission_required('orders.view_order', raise_exception=True)
def order_print(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'items', 'payments'
        ).select_related('customer', 'created_by'),
        pk=pk
    )
    company = CompanySetting.get_settings()
    context = {
        'order': order,
        'company': company,
        'title': _('طباعة الطلب: %s') % order.order_number,
    }
    return render(request, 'orders/order_print.html', context)


@login_required
@permission_required('orders.add_deliverynote', raise_exception=True)
def add_delivery_note(request, pk):
    return delivery_note_create(request, pk)


@login_required
@permission_required('orders.view_order', raise_exception=True)
def payment_receipt(request, pk, payment_pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)
    payment = get_object_or_404(OrderPayment, pk=payment_pk, order=order)
    company = CompanySetting.get_settings()
    context = {
        'payment': payment,
        'company': company,
        'title': _('سند قبض: %s') % order.order_number,
    }
    return render(request, 'orders/payment_receipt.html', context)
