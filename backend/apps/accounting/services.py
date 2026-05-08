from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from .models import Account, JournalEntry, JournalLine


def post_order_revenue(order, user):
    from apps.orders.models import Order

    if JournalEntry.objects.filter(reference_type='order', reference_id=order.pk).exists():
        return None

    with transaction.atomic():
        entry = JournalEntry.objects.create(
            entry_date=order.order_date.date(),
            description=f'إيراد أمر شغل {order.order_number} - {order.customer}',
            reference_type='order',
            reference_id=order.pk,
            status='posted',
            posted_at=timezone.now(),
            created_by=user,
        )

        revenue_account = Account.objects.get(code='41')
        tax_account = Account.objects.get(code='2104')

        revenue_items = order.items.filter(item_type__in=['printing', 'laser', 'engraving'])
        other_items = order.items.exclude(item_type__in=['printing', 'laser', 'engraving'])

        revenue_total = sum(item.total for item in revenue_items) if revenue_items else Decimal('0')
        other_total = sum(item.total for item in other_items) if other_items else Decimal('0')

        discount_amount = Decimal('0')
        if order.discount_type == 'percentage':
            discount_amount = order.subtotal * (order.discount_value / 100) if order.subtotal else Decimal('0')
        elif order.discount_type == 'fixed':
            discount_amount = order.discount_value

        net_revenue = order.subtotal - discount_amount

        if net_revenue > 0:
            revenue_entries = []
            if revenue_items:
                revenue_entries.append((revenue_account, net_revenue))
            elif other_items:
                design_acc = Account.objects.get(code='42')
                revenue_entries.append((design_acc, net_revenue))

            for acc, amount in revenue_entries:
                JournalLine.objects.create(
                    entry=entry, account=acc, credit=amount,
                    description=f'إيراد {order.order_number}',
                )

        if order.tax_amount > 0:
            JournalLine.objects.create(
                entry=entry, account=tax_account, credit=order.tax_amount,
                description=f'ضريبة {order.order_number}',
            )

        total_credit = sum(line.credit for line in entry.lines.all())
        if total_credit > 0:
            receivable = Account.objects.get(code='1104')
            JournalLine.objects.create(
                entry=entry, account=receivable, debit=total_credit,
                description=f'عميل: {order.customer}',
            )

        if not entry.is_balanced():
            entry.status = 'draft'
            entry.save(update_fields=['status'])

    return entry


def post_pos_revenue(sale, user):
    if JournalEntry.objects.filter(reference_type='pos', reference_id=sale.pk).exists():
        return None

    with transaction.atomic():
        entry = JournalEntry.objects.create(
            entry_date=sale.sale_date.date(),
            description=f'إيراد مبيعات نقدية {sale.sale_number}',
            reference_type='pos',
            reference_id=sale.pk,
            status='posted',
            posted_at=timezone.now(),
            created_by=user,
        )

        cash = Account.objects.get(code='1101')
        revenue = Account.objects.get(code='43')
        tax = Account.objects.get(code='2104')

        net_sale = sale.subtotal - sale.discount

        JournalLine.objects.create(
            entry=entry, account=cash, debit=sale.total,
            description=f'مبيعات نقدية {sale.sale_number}',
        )
        JournalLine.objects.create(
            entry=entry, account=revenue, credit=net_sale,
            description=f'إيراد {sale.sale_number}',
        )
        if sale.tax > 0:
            JournalLine.objects.create(
                entry=entry, account=tax, credit=sale.tax,
                description=f'ضريبة {sale.sale_number}',
            )

    return entry


def post_cogs(reference_type, reference_id, user=None):
    from apps.inventory.models import InventoryValuation

    if JournalEntry.objects.filter(reference_type=f'cogs_{reference_type}', reference_id=reference_id).exists():
        return None

    valuations = InventoryValuation.objects.filter(
        reference_type=reference_type, reference_id=reference_id
    )
    if not valuations.exists():
        return None

    total_cost = sum(v.total_cost for v in valuations)

    with transaction.atomic():
        entry = JournalEntry.objects.create(
            entry_date=timezone.now().date(),
            description=f'تكلفة بضاعة مباعة {reference_type}#{reference_id}',
            reference_type=f'cogs_{reference_type}',
            reference_id=reference_id,
            status='posted',
            posted_at=timezone.now(),
            created_by=user,
        )

        cogs = Account.objects.get(code='51')
        inventory = Account.objects.get(code='1105')

        JournalLine.objects.create(
            entry=entry, account=cogs, debit=total_cost,
            description=f'COGS {reference_type}#{reference_id}',
        )
        JournalLine.objects.create(
            entry=entry, account=inventory, credit=total_cost,
            description=f'مخزون خامات {reference_type}#{reference_id}',
        )

    return entry
