from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import app_permission_required
from django.db.models import Q, Sum, F
from django.shortcuts import get_object_or_404, redirect, render

from django.core.paginator import Paginator

from .forms import CategoryForm, MaterialForm, StockAdjustmentForm, StockTransferForm
from .models import Batch, Category, Material, StockMovement


@app_permission_required('inventory_view')
def material_list(request):
    materials = Material.objects.select_related('category').all()
    category_id = request.GET.get('category')
    search = request.GET.get('q')
    low_stock = request.GET.get('low_stock')

    if category_id:
        materials = materials.filter(category_id=category_id)
    if search:
        materials = materials.filter(
            Q(code__icontains=search) | Q(name__icontains=search) | Q(name_ar__icontains=search)
        )
    if low_stock:
        materials = materials.filter(current_stock__lte=F('minimum_stock'))

    categories = Category.objects.all()
    low_stock_count = Material.objects.filter(current_stock__lte=F('minimum_stock')).count()

    context = {
        'materials': materials,
        'categories': categories,
        'low_stock_count': low_stock_count,
        'title': 'الخامات',
    }
    return render(request, 'inventory/material_list.html', context)


@app_permission_required('inventory_view')
def material_detail(request, pk):
    material = get_object_or_404(Material.objects.select_related('category'), pk=pk)
    batches = material.batches.all()
    movements = material.stock_movements.select_related('created_by').all()[:50]

    context = {
        'material': material,
        'batches': batches,
        'movements': movements,
        'title': f'خامة - {material.name_ar or material.name}',
    }
    return render(request, 'inventory/material_detail.html', context)


@app_permission_required('inventory_create')
def material_create(request):
    if request.method == 'POST':
        form = MaterialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الخامة بنجاح')
            return redirect('inventory:material_list')
    else:
        form = MaterialForm()

    context = {'form': form, 'title': 'إضافة خامة'}
    return render(request, 'inventory/material_form.html', context)


@app_permission_required('inventory_edit')
def material_edit(request, pk):
    material = get_object_or_404(Material, pk=pk)
    if request.method == 'POST':
        form = MaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الخامة بنجاح')
            return redirect('inventory:material_detail', pk=material.pk)
    else:
        form = MaterialForm(instance=material)

    context = {'form': form, 'title': 'تعديل خامة'}
    return render(request, 'inventory/material_form.html', context)


@app_permission_required('inventory_view')
def batch_list(request):
    batches = Batch.objects.select_related('material', 'supplier').all()
    material_id = request.GET.get('material')
    search = request.GET.get('q')

    if material_id:
        batches = batches.filter(material_id=material_id)
    if search:
        batches = batches.filter(
            Q(batch_number__icontains=search) | Q(material__name__icontains=search)
        )

    context = {
        'batches': batches,
        'materials': Material.objects.filter(is_active=True),
        'title': 'الدفعات',
    }
    return render(request, 'inventory/batch_list.html', context)


@app_permission_required('inventory_manage_stock')
def batch_create(request):
    if request.method == 'POST':
        from apps.suppliers.models import Supplier
        material_id = request.POST.get('material')
        supplier_id = request.POST.get('supplier')
        batch_number = request.POST.get('batch_number')
        quantity = request.POST.get('quantity')
        unit_price = request.POST.get('unit_price')
        purchase_date = request.POST.get('purchase_date')
        notes = request.POST.get('notes', '')

        material = get_object_or_404(Material, pk=material_id)
        supplier = Supplier.objects.filter(pk=supplier_id).first() if supplier_id else None

        batch = Batch.objects.create(
            batch_number=batch_number,
            material=material,
            supplier=supplier,
            quantity=quantity,
            remaining_quantity=quantity,
            unit_price=unit_price,
            purchase_date=purchase_date,
            notes=notes,
        )

        StockMovement.objects.create(
            material=material,
            batch=batch,
            movement_type='purchase_in',
            quantity=quantity,
            unit_price=unit_price,
            notes=notes,
            created_by=request.user,
        )

        material.current_stock = F('current_stock') + float(quantity)
        material.save()

        messages.success(request, 'تم إضافة الدفعة بنجاح')
        return redirect('inventory:batch_list')

    from apps.suppliers.models import Supplier
    materials = Material.objects.filter(is_active=True)
    suppliers = Supplier.objects.filter(is_active=True)
    context = {
        'materials': materials,
        'suppliers': suppliers,
        'title': 'إضافة دفعة',
    }
    return render(request, 'inventory/batch_form.html', context)


@app_permission_required('inventory_view')
def stock_movement_list(request):
    movements = StockMovement.objects.select_related('material', 'batch', 'created_by').all()
    material_id = request.GET.get('material')
    movement_type = request.GET.get('movement_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if material_id:
        movements = movements.filter(material_id=material_id)
    if movement_type:
        movements = movements.filter(movement_type=movement_type)
    if date_from:
        movements = movements.filter(created_at__date__gte=datetime.strptime(date_from, '%Y-%m-%d').date())
    if date_to:
        movements = movements.filter(created_at__date__lte=datetime.strptime(date_to, '%Y-%m-%d').date())

    context = {
        'movements': movements,
        'materials': Material.objects.filter(is_active=True),
        'title': 'الحركات المخزنية',
    }
    return render(request, 'inventory/stock_movement_list.html', context)


@app_permission_required('inventory_manage_stock')
def stock_adjustment(request):
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.created_by = request.user
            movement.save()

            material = movement.material
            if movement.quantity > 0:
                material.current_stock = F('current_stock') + movement.quantity
            else:
                material.current_stock = F('current_stock') + movement.quantity
            material.save()

            messages.success(request, 'تم تسجيل التسوية بنجاح')
            return redirect('inventory:stock_movement_list')
    else:
        form = StockAdjustmentForm()

    context = {'form': form, 'title': 'تسوية مخزنية'}
    return render(request, 'inventory/material_form.html', context)


@app_permission_required('inventory_view')
def inventory_report(request):
    materials = Material.objects.select_related('category').all()
    total_value = sum(m.current_stock * m.purchase_price for m in materials)
    total_items = materials.count()
    low_stock_items = materials.filter(current_stock__lte=F('minimum_stock')).count()

    paginator = Paginator(materials, 25)
    page_number = request.GET.get('page')
    materials_page = paginator.get_page(page_number)

    context = {
        'materials': materials_page,
        'total_value': total_value,
        'total_items': total_items,
        'low_stock_items': low_stock_items,
        'title': 'تقرير المخزون',
    }
    return render(request, 'inventory/material_list.html', context)


@app_permission_required('inventory_view')
def low_stock_report(request):
    materials = Material.objects.filter(current_stock__lte=F('minimum_stock')).select_related('category')

    paginator = Paginator(materials, 25)
    page_number = request.GET.get('page')
    materials_page = paginator.get_page(page_number)

    context = {
        'materials': materials_page,
        'is_low_stock': True,
        'title': 'تنبيه نفاد المخزون',
    }
    return render(request, 'inventory/material_list.html', context)


@app_permission_required('inventory_manage_stock')
def stock_movement_create(request):
    if request.method == 'POST':
        material_id = request.POST.get('material')
        movement_type = request.POST.get('movement_type')
        quantity = request.POST.get('quantity')
        notes = request.POST.get('notes', '')

        material = get_object_or_404(Material, pk=material_id)
        qty = float(quantity)
        if movement_type in ['sale_out', 'usage_out', 'damage_out', 'transfer_out', 'adjustment_out', 'production_out']:
            qty = -abs(qty)

        StockMovement.objects.create(
            material=material,
            movement_type=movement_type,
            quantity=qty,
            notes=notes,
            created_by=request.user,
        )

        material.current_stock = F('current_stock') + qty
        material.save()

        messages.success(request, 'تم تسجيل الحركة بنجاح')
        return redirect('inventory:stock_movement_list')

    materials = Material.objects.filter(is_active=True)
    context = {
        'materials': materials,
        'title': 'حركة مخزنية جديدة',
    }
    return render(request, 'inventory/batch_form.html', context)
