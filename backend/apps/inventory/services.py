from decimal import Decimal

from django.db import transaction
from django.db.models import F

from .models import Batch, InventoryValuation, Material, StockMovement


def deduct_stock_fifo(material, quantity, reference_type=None, reference_id=None, notes='', user=None):
    if quantity <= 0:
        return []

    batches = Batch.objects.filter(
        material=material, remaining_quantity__gt=0
    ).order_by('purchase_date', 'id')

    remaining = Decimal(str(quantity))
    valuations = []

    with transaction.atomic():
        for batch in batches:
            if remaining <= 0:
                break

            deduct = min(remaining, batch.remaining_quantity)
            unit_cost = batch.unit_price
            total_cost = deduct * unit_cost

            InventoryValuation.objects.create(
                batch=batch,
                material=material,
                quantity=deduct,
                unit_cost=unit_cost,
                total_cost=total_cost,
                method='fifo',
                reference_type=reference_type,
                reference_id=reference_id,
            )

            Batch.objects.filter(pk=batch.pk).update(
                remaining_quantity=F('remaining_quantity') - deduct
            )

            StockMovement.objects.create(
                material=material,
                batch=batch,
                movement_type='sale_out',
                quantity=-deduct,
                unit_price=unit_cost,
                reference_type=reference_type,
                reference_id=reference_id,
                notes=notes,
                created_by=user,
            )

            valuations.append({
                'batch': batch,
                'quantity': deduct,
                'unit_cost': unit_cost,
                'total_cost': total_cost,
            })

            remaining -= deduct

        if remaining > 0:
            raise ValueError(
                f'رصيد غير كافٍ للخامة {material.name_ar or material.name}. '
                f'المطلوب: {quantity}, المتاح: {quantity - remaining}'
            )

        Material.objects.filter(pk=material.pk).update(
            current_stock=F('current_stock') - quantity
        )

    return valuations


def reverse_stock_deduction(reference_type, reference_id, user=None):
    valuations = InventoryValuation.objects.filter(
        reference_type=reference_type, reference_id=reference_id
    )
    if not valuations.exists():
        return False

    with transaction.atomic():
        for val in valuations:
            Batch.objects.filter(pk=val.batch_id).update(
                remaining_quantity=F('remaining_quantity') + val.quantity
            )

            Material.objects.filter(pk=val.material_id).update(
                current_stock=F('current_stock') + val.quantity
            )

            StockMovement.objects.create(
                material_id=val.material_id,
                batch_id=val.batch_id,
                movement_type='return_in',
                quantity=val.quantity,
                unit_price=val.unit_cost,
                reference_type=f'reverse_{reference_type}',
                reference_id=reference_id,
                notes=f'إلغاء صرف: {reference_type}#{reference_id}',
                created_by=user,
            )

        valuations.delete()

    return True
