from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Order, OrderPayment
from apps.inventory.services import deduct_stock_fifo, reverse_stock_deduction
from apps.accounting.services import post_order_revenue, post_pos_revenue, post_cogs


def update_order_payment_status(order):
    """
    Update order payment status fields based on payments.
    Called after adding/removing payments.
    """
    if order.subtotal == 0 and order.items.exists():
        order.calculate_totals()
    total_paid = sum(p.amount for p in order.payments.all())
    order.paid_amount = total_paid
    order.due_amount = order.total - total_paid
    if total_paid <= 0:
        order.payment_status = order.PaymentStatus.UNPAID
    elif total_paid >= order.total:
        order.payment_status = order.PaymentStatus.PAID
    else:
        order.payment_status = order.PaymentStatus.PARTIAL
    order.save(update_fields=['paid_amount', 'due_amount', 'payment_status'])


def adjust_customer_balance_for_order(order, delta_total):
    """
    Adjust customer balance when order total changes.
    Positive delta increases customer balance (customer owes more).
    """
    customer = order.customer
    customer.current_balance += delta_total
    customer.save(update_fields=['current_balance'])


def adjust_customer_balance_for_payment(payment):
    """
    Adjust customer balance when a payment is added/removed.
    Payment received decreases customer balance (customer owes less).
    """
    customer = payment.order.customer
    customer.current_balance -= payment.amount
    customer.save(update_fields=['current_balance'])


def create_order_payment(order, amount, payment_date, payment_method, reference, notes, user):
    """
    Create an order payment and update related balances/status.
    """
    with transaction.atomic():
        payment = OrderPayment.objects.create(
            order=order,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            created_by=user
        )
        adjust_customer_balance_for_payment(payment)
        update_order_payment_status(payment.order)
        return payment


@transaction.atomic
def confirm_order(order, user=None):
    """
    Confirm an order: deduct inventory, post revenue.
    """
    # Deduct inventory for all material items
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
                user=user
            )
            post_cogs('order', order.pk, user=user)
    
    # Post revenue
    post_order_revenue(order, user)
    
    order.status = order.Status.CONFIRMED
    order.save()
    return order


@transaction.atomic
def cancel_order(order, user=None):
    """
    Cancel an order: reverse inventory, adjust balance.
    """
    # Reverse inventory if order was confirmed/in_production
    if order.status in (order.Status.CONFIRMED, order.Status.IN_PRODUCTION):
        reverse_stock_deduction('order', order.pk, user=user)
    
    # Adjust customer balance (remove the order total)
    customer = order.customer
    customer.current_balance -= order.total
    customer.save(update_fields=['current_balance'])
    
    order.status = order.Status.CANCELLED
    order.save()
    return order