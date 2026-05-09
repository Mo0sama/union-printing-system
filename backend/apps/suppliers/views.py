from datetime import datetime

from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import app_permission_required

from .forms import PurchaseOrderForm, SupplierForm, SupplierPaymentForm
from .models import PurchaseOrder, PurchaseOrderItem, Supplier


@app_permission_required('suppliers_view')
def supplier_list(request):
    suppliers = Supplier.objects.all()
    search = request.GET.get('q')
    supply_type = request.GET.get('supply_type')
    active_only = request.GET.get('active_only')

    if search:
        suppliers = suppliers.filter(
            Q(company_name__icontains=search) | Q(contact_person__icontains=search) |
            Q(phone__icontains=search) | Q(code__icontains=search)
        )
    if supply_type:
        suppliers = suppliers.filter(supply_type=supply_type)
    if active_only:
        suppliers = suppliers.filter(is_active=True)

    supply_types = Supplier.objects.values_list('supply_type', flat=True).distinct()

    context = {
        'suppliers': suppliers,
        'supply_types': supply_types,
        'title': 'الموردين',
    }
    return render(request, 'suppliers/supplier_list.html', context)


@app_permission_required('suppliers_view')
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    purchase_orders = supplier.purchase_orders.all()
    payments = supplier.payments.all()

    total_orders = purchase_orders.aggregate(total=Sum('total'))['total'] or 0
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
    context = {
        'supplier': supplier,
        'purchase_orders': purchase_orders,
        'purchase_orders_total': total_orders,
        'payments': payments,
        'payments_total': total_payments,
        'title': f'مورد - {supplier.company_name}',
    }
    return render(request, 'suppliers/supplier_detail.html', context)


@app_permission_required('suppliers_create')
def supplier_create(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.created_by = request.user
            supplier.save()
            messages.success(request, 'تم إضافة المورد بنجاح')
            return redirect('suppliers:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm()

    context = {'form': form, 'title': 'إضافة مورد'}
    return render(request, 'suppliers/supplier_form.html', context)


@app_permission_required('suppliers_edit')
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المورد بنجاح')
            return redirect('suppliers:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierForm(instance=supplier)

    context = {'form': form, 'title': 'تعديل مورد'}
    return render(request, 'suppliers/supplier_form.html', context)


@app_permission_required('suppliers_delete')
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.is_active = False
        supplier.save()
        messages.success(request, 'تم حذف المورد بنجاح')
        return redirect('suppliers:supplier_list')

    context = {'supplier': supplier, 'title': 'حذف مورد'}
    return render(request, 'suppliers/supplier_confirm_delete.html', context)


@app_permission_required('purchase_orders_view')
def purchase_order_list(request):
    orders = PurchaseOrder.objects.select_related('supplier', 'created_by').all()
    supplier_id = request.GET.get('supplier')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('q')

    if supplier_id:
        orders = orders.filter(supplier_id=supplier_id)
    if status:
        orders = orders.filter(status=status)
    if date_from:
        orders = orders.filter(order_date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        orders = orders.filter(order_date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())
    if search:
        orders = orders.filter(Q(po_number__icontains=search) | Q(supplier__company_name__icontains=search))

    context = {
        'orders': orders,
        'suppliers': Supplier.objects.filter(is_active=True),
        'title': 'أوامر الشراء',
    }
    return render(request, 'suppliers/purchase_order_list.html', context)


@app_permission_required('purchase_orders_view')
def purchase_order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder.objects.select_related('supplier', 'created_by'), pk=pk)
    items = order.items.select_related('material').all()

    context = {
        'order': order,
        'items': items,
        'title': f'أمر شراء - {order.po_number}',
    }
    return render(request, 'suppliers/purchase_order_detail.html', context)


@app_permission_required('purchase_orders_create')
def purchase_order_create(request):
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()

            materials = request.POST.getlist('material[]')
            quantities = request.POST.getlist('quantity[]')
            unit_prices = request.POST.getlist('unit_price[]')
            totals = request.POST.getlist('total[]')

            for i in range(len(materials)):
                if materials[i]:
                    PurchaseOrderItem.objects.create(
                        purchase_order=order,
                        material_id=materials[i],
                        quantity=quantities[i],
                        unit_price=unit_prices[i],
                        total=totals[i],
                    )

            order.save()
            messages.success(request, 'تم إنشاء أمر الشراء بنجاح')
            return redirect('suppliers:purchase_order_detail', pk=order.pk)
    else:
        form = PurchaseOrderForm()

    from apps.inventory.models import Material
    materials = Material.objects.filter(is_active=True)

    context = {
        'form': form,
        'materials': materials,
        'title': 'إنشاء أمر شراء',
    }
    return render(request, 'suppliers/purchase_order_form.html', context)


@app_permission_required('purchase_orders_receive')
def purchase_order_receive(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == 'POST':
        from apps.inventory.models import Batch, StockMovement
        items = order.items.all()
        for item in items:
            received_qty = float(request.POST.get(f'received_{item.pk}', 0))
            if received_qty > 0:
                item.received_quantity = received_qty
                item.save()

                batch = Batch.objects.create(
                    batch_number=f'PO-{order.po_number}-{item.pk}',
                    material=item.material,
                    supplier=order.supplier,
                    quantity=received_qty,
                    remaining_quantity=received_qty,
                    unit_price=item.unit_price,
                    purchase_date=order.order_date,
                )

                StockMovement.objects.create(
                    material=item.material,
                    batch=batch,
                    movement_type='purchase_in',
                    quantity=received_qty,
                    unit_price=item.unit_price,
                    reference_type='purchase_order',
                    reference_id=order.pk,
                    created_by=request.user,
                )

                item.material.current_stock += received_qty
                item.material.save()

        order.status = 'received'
        order.save()
        messages.success(request, 'تم استلام أمر الشراء بنجاح')
        return redirect('suppliers:purchase_order_detail', pk=order.pk)

    context = {
        'order': order,
        'items': order.items.all(),
        'title': 'استلام أمر شراء',
    }
    return render(request, 'suppliers/purchase_order_detail.html', context)


@app_permission_required('purchase_orders_edit')
def add_supplier_payment(request, supplier_pk):
    supplier = get_object_or_404(Supplier, pk=supplier_pk)
    if request.method == 'POST':
        form = SupplierPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.supplier = supplier
            payment.created_by = request.user
            payment.save()

            if payment.purchase_order:
                payment.purchase_order.paid_amount += payment.amount
                payment.purchase_order.save()

            supplier.current_balance += payment.amount
            supplier.save()

            messages.success(request, 'تم إضافة الدفعة بنجاح')
            return redirect('suppliers:supplier_detail', pk=supplier.pk)
    else:
        form = SupplierPaymentForm(initial={'supplier': supplier})

    context = {'form': form, 'supplier': supplier, 'title': 'إضافة دفعة'}
    return render(request, 'suppliers/supplier_form.html', context)


@app_permission_required('suppliers_view')
def supplier_ledger(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    transactions = []

    payments = supplier.payments.all()
    if date_from:
        payments = payments.filter(payment_date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        payments = payments.filter(payment_date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())

    for p in payments:
        transactions.append({
            'date': p.payment_date,
            'type': 'دفعة',
            'reference': p.reference or f'دفعة #{p.pk}',
            'debit': 0,
            'credit': p.amount,
            'balance': 0,
        })

    orders = supplier.purchase_orders.all()
    for o in orders:
        transactions.append({
            'date': o.order_date,
            'type': 'أمر شراء',
            'reference': o.po_number,
            'debit': o.total,
            'credit': 0,
            'balance': 0,
        })

    transactions.sort(key=lambda x: x['date'])
    balance = 0
    for t in transactions:
        balance += t['debit'] - t['credit']
        t['balance'] = balance

    total_orders = orders.aggregate(total=Sum('total'))['total'] or 0
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0
    context = {
        'supplier': supplier,
        'transactions': transactions,
        'purchase_orders': orders,
        'payments': payments,
        'purchase_orders_total': total_orders,
        'payments_total': total_payments,
        'title': f'كشف حساب - {supplier.company_name}',
    }
    return render(request, 'suppliers/supplier_detail.html', context)
