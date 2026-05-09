import json
from contextlib import suppress
from decimal import Decimal

from django.contrib import messages
from django.db.models import DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.accounting.services import post_cogs, post_pos_revenue
from apps.accounts.decorators import app_permission_required
from apps.inventory.models import Material
from apps.inventory.services import deduct_stock_fifo, reverse_stock_deduction

from .forms import POSCloseForm, POSSessionForm
from .models import POSSale, POSSaleItem, POSSession
from .services import adjust_customer_balance


@app_permission_required('pos_view')
def pos_dashboard(request):
    open_session = POSSession.objects.filter(status='open').first()
    if not open_session:
        return redirect('pos:pos_session_open')

    today_sales = POSSale.objects.filter(
        session=open_session, status='completed'
    ).order_by('-sale_date')

    today_total = today_sales.aggregate(
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField())
    )['total']

    recent_sales = today_sales[:20]
    sale_count = today_sales.count()

    from apps.customers.models import Customer
    from apps.inventory.models import Material
    products = Material.objects.filter(is_active=True)[:50]
    customers = Customer.objects.filter(is_active=True)[:50]

    context = {
        'session': open_session,
        'recent_sales': recent_sales,
        'today_total': today_total,
        'sale_count': sale_count,
        'products': products,
        'customers': customers,
        'title': 'نقطة البيع',
    }
    return render(request, 'pos/pos_dashboard.html', context)


@app_permission_required('pos_manage_sessions')
def pos_session_open(request):
    if POSSession.objects.filter(status='open').exists():
        messages.warning(request, 'توجد جلسة مفتوحة بالفعل')
        return redirect('pos:pos_dashboard')

    if request.method == 'POST':
        form = POSSessionForm(request.POST)
        if form.is_valid():
            session = form.save()
            messages.success(request, f'تم فتح الجلسة {session.session_number}')
            return redirect('pos:pos_dashboard')
    else:
        form = POSSessionForm()
    context = {
        'form': form,
        'title': 'فتح جلسة جديدة',
    }
    return render(request, 'pos/pos_session_form.html', context)


@app_permission_required('pos_manage_sessions')
def pos_session_close(request, pk):
    session = get_object_or_404(POSSession, pk=pk)
    if session.status == 'closed':
        messages.warning(request, 'الجلسة مغلقة بالفعل')
        return redirect('pos:pos_session_list')

    sales = POSSale.objects.filter(session=session, status='completed')
    total_sales = sales.aggregate(
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField())
    )['total']
    sale_count = sales.count()
    expected = session.opening_balance + total_sales

    if request.method == 'POST':
        form = POSCloseForm(request.POST, instance=session)
        if form.is_valid():
            session = form.save(commit=False)
            session.expected_balance = expected
            if session.closing_balance is not None:
                session.difference = session.closing_balance - expected
            session.closed_at = timezone.now()
            session.status = 'closed'
            session.save()
            messages.success(request, f'تم إغلاق الجلسة {session.session_number}')
            return redirect('pos:pos_session_list')
    else:
        form = POSCloseForm(instance=session)

    context = {
        'form': form,
        'session': session,
        'total_sales': total_sales,
        'sale_count': sale_count,
        'expected_balance': expected,
        'title': 'إغلاق الجلسة',
    }
    return render(request, 'pos/pos_session_close.html', context)


@app_permission_required('pos_manage_sessions')
def pos_session_list(request):
    sessions = POSSession.objects.select_related('cashier').all().order_by('-opened_at')
    context = {
        'sessions': sessions,
        'title': 'جلسات البيع',
    }
    return render(request, 'pos/pos_session_list.html', context)


@app_permission_required('pos_create')
def pos_sale_create(request):
    open_session = POSSession.objects.filter(status='open').first()
    if not open_session:
        messages.error(request, 'يجب فتح جلسة بيع أولاً')
        return redirect('pos:pos_session_open')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, AttributeError):
            data = request.POST

        items_raw = data.get('items', [])
        items_data = json.loads(items_raw) if isinstance(items_raw, str) else items_raw
        if not items_data:
            return JsonResponse({'success': False, 'error': 'لا توجد أصناف'})

        customer_id = data.get('customer_id', None)
        payment_method = data.get('payment_method', 'cash')
        notes = data.get('notes', '')
        paid_amount = Decimal(str(data.get('paid_amount', 0)))
        discount = Decimal(str(data.get('discount', 0)))
        tax_percent = Decimal(str(data.get('tax_percent', 0)))

        subtotal = Decimal('0')
        items = []
        for item_data in items_data:
            material_id = item_data.get('id')
            qty = Decimal(str(item_data.get('qty', item_data.get('quantity', 1))))
            material = None
            if material_id:
                with suppress(Material.DoesNotExist):
                    material = Material.objects.get(pk=material_id)
            price = Decimal(str(item_data.get('price', item_data.get('unit_price', 0))))
            if material and not price:
                price = material.selling_price or Decimal('0')
            total = qty * price
            subtotal += total
            items.append({
                'material': material,
                'item_type': 'material' if material else item_data.get('item_type', 'product'),
                'description': item_data.get('description', item_data.get('name', material.name if material else '')),
                'quantity': int(qty),
                'unit_price': price,
                'total': total,
            })

        tax = subtotal * tax_percent / Decimal('100')
        total = subtotal - discount + tax
        change_amount = max(Decimal('0'), paid_amount - total)

        sale = POSSale.objects.create(
            session=open_session,
            customer_id=customer_id if customer_id else None,
            subtotal=subtotal,
            discount=discount,
            tax=tax,
            total=total,
            paid_amount=paid_amount,
            change_amount=change_amount,
            payment_method=payment_method,
            notes=notes,
            created_by=request.user,
        )

        for item in items:
            sale_item = POSSaleItem.objects.create(
                sale=sale,
                material=item['material'],
                item_type=item['item_type'],
                description=item['description'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total=item['total'],
            )
            if item['material']:
                deduct_stock_fifo(
                    material=item['material'],
                    quantity=sale_item.quantity,
                    reference_type='pos',
                    reference_id=sale.pk,
                    notes=f'{sale.sale_number} - {sale_item.description}',
                    user=request.user,
                )
                post_cogs('pos', sale.pk, user=request.user)

        post_pos_revenue(sale, request.user)

        if sale.customer:
            adjust_customer_balance(sale.customer, sale.total)

        return JsonResponse({
            'success': True,
            'sale_id': sale.id,
            'sale_number': sale.sale_number,
            'total': float(total),
            'paid_amount': float(paid_amount),
            'change_amount': float(change_amount),
            'receipt_url': f'/pos/receipt/{sale.id}/',
        })

    context = {
        'session': open_session,
        'title': 'فاتورة جديدة',
    }
    return render(request, 'pos/pos_sale_form.html', context)


@app_permission_required('pos_view')
def pos_sale_detail(request, pk):
    sale = get_object_or_404(
        POSSale.objects.select_related('session', 'customer', 'created_by'),
        pk=pk
    )
    items = sale.items.all()
    context = {
        'sale': sale,
        'items': items,
        'title': f'فاتورة {sale.sale_number}',
    }
    return render(request, 'pos/pos_sale_detail.html', context)


@require_POST
@app_permission_required('pos_refund')
def pos_sale_refund(request, pk):
    sale = get_object_or_404(POSSale, pk=pk)
    if sale.status == 'refunded':
        messages.warning(request, 'تم استرجاع هذه الفاتورة مسبقاً')
    elif sale.status == 'voided':
        messages.warning(request, 'هذه الفاتورة ملغاة')
    else:
        sale.status = 'refunded'
        sale.save()
        reverse_stock_deduction('pos', sale.pk, user=request.user)
        if sale.customer:
            adjust_customer_balance(sale.customer, -sale.total)
        messages.success(request, f'تم استرجاع الفاتورة {sale.sale_number}')
    return redirect('pos:pos_sale_detail', pk=sale.pk)


@app_permission_required('pos_view')
def pos_sale_list(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    status_filter = request.GET.get('status', '')

    sales = POSSale.objects.select_related('session', 'customer').all()

    if date_from:
        sales = sales.filter(sale_date__date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__date__lte=date_to)
    if status_filter:
        sales = sales.filter(status=status_filter)

    total_amount = sales.aggregate(
        total=Coalesce(Sum('total'), Value(0), output_field=DecimalField())
    )['total']

    context = {
        'sales': sales,
        'date_from': date_from,
        'date_to': date_to,
        'status_filter': status_filter,
        'total_amount': total_amount,
        'title': 'فواتير البيع',
    }
    return render(request, 'pos/pos_sale_list.html', context)


@app_permission_required('pos_view')
def pos_receipt(request, pk):
    sale = get_object_or_404(
        POSSale.objects.select_related('session__cashier', 'customer', 'created_by'),
        pk=pk
    )
    items = sale.items.all()
    context = {
        'sale': sale,
        'items': items,
        'title': 'إيصال',
    }
    return render(request, 'pos/pos_receipt.html', context)


@app_permission_required('pos_view')
def pos_get_items(request):
    q = request.GET.get('q', '')
    products = Material.objects.filter(
        Q(name__icontains=q) | Q(code__icontains=q)
    )[:20] if q else Material.objects.all()[:50]

    data = [{
        'id': p.id,
        'name': p.name,
        'barcode': p.code or '',
        'price': float(p.selling_price),
        'stock': float(p.current_stock) if hasattr(p, 'current_stock') else 0,
    } for p in products]
    return JsonResponse({'items': data})
