from decimal import Decimal
from django.db import transaction
from .models import Customer, CustomerPayment


def adjust_balance(customer, delta_amount):
    customer.current_balance += delta_amount
    customer.save(update_fields=['current_balance'])


def record_customer_payment(customer, amount, payment_date, payment_method, reference, notes, user):
    with transaction.atomic():
        payment = CustomerPayment.objects.create(
            customer=customer,
            amount=amount,
            payment_date=payment_date,
            payment_method=payment_method,
            reference=reference,
            notes=notes,
            created_by=user,
        )
        adjust_balance(customer, -amount)
        return payment