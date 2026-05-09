from django.db import transaction

from apps.accounting.services import post_cogs
from apps.inventory.services import deduct_stock_fifo, reverse_stock_deduction

from .models import POSSaleItem


def adjust_customer_balance(customer, delta):
    customer.current_balance += delta
    customer.save(update_fields=['current_balance'])


def process_sale_items(sale, items_data, user=None):
    for item_data in items_data:
        sale_item = POSSaleItem.objects.create(
            sale=sale,
            material=item_data.get('material'),
            item_type=item_data.get('item_type', 'product'),
            description=item_data.get('description', ''),
            quantity=item_data.get('quantity', 1),
            unit_price=item_data.get('unit_price', 0),
            total=item_data.get('total', 0),
        )
        if sale_item.material:
            deduct_stock_fifo(
                material=sale_item.material,
                quantity=sale_item.quantity,
                reference_type='pos',
                reference_id=sale.pk,
                notes=f'{sale.sale_number} - {sale_item.description}',
                user=user,
            )
            post_cogs('pos', sale.pk, user=user)


def refund_sale(sale, user=None):
    with transaction.atomic():
        sale.status = 'refunded'
        sale.save()
        reverse_stock_deduction('pos', sale.pk, user=user)
        if sale.customer:
            adjust_customer_balance(sale.customer, -sale.total)
    return sale
