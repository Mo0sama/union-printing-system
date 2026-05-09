from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.customers.models import Customer

from .models import Order, OrderPayment
from .services import (
    adjust_customer_balance_for_order,
    adjust_customer_balance_for_payment,
    update_order_payment_status,
)

User = get_user_model()


class OrderBalanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.customer = Customer.objects.create(
            name='Test Customer', phone='01000000000', created_by=self.user
        )
        self.order = Order.objects.create(
            customer=self.customer,
            delivery_date=timezone.now().date() + timezone.timedelta(days=7),
            subtotal=Decimal('1000'),
            total=Decimal('1000'),
            paid_amount=Decimal('0'),
            due_amount=Decimal('1000'),
            created_by=self.user,
        )

    def test_create_order_increases_balance(self):
        old_balance = self.customer.current_balance
        adjust_customer_balance_for_order(self.order, Decimal('1000'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, old_balance + Decimal('1000'))

    def test_delete_order_decreases_balance(self):
        adjust_customer_balance_for_order(self.order, Decimal('1000'))
        adjust_customer_balance_for_order(self.order, -Decimal('1000'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('0'))

    def test_edit_order_adjusts_balance(self):
        adjust_customer_balance_for_order(self.order, Decimal('1000'))
        adjust_customer_balance_for_order(self.order, Decimal('500'))  # total increased by 500
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('1500'))

    def test_add_payment_decreases_balance(self):
        adjust_customer_balance_for_order(self.order, Decimal('1000'))
        payment = OrderPayment.objects.create(
            order=self.order,
            amount=Decimal('300'),
            payment_date=timezone.now().date(),
            created_by=self.user,
        )
        adjust_customer_balance_for_payment(payment)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('700'))

    def test_multiple_payments(self):
        adjust_customer_balance_for_order(self.order, Decimal('1000'))
        p1 = OrderPayment.objects.create(order=self.order, amount=Decimal('200'), created_by=self.user)
        adjust_customer_balance_for_payment(p1)
        p2 = OrderPayment.objects.create(order=self.order, amount=Decimal('300'), created_by=self.user)
        adjust_customer_balance_for_payment(p2)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('500'))

    def test_cancel_order_reverses_balance(self):
        adjust_customer_balance_for_order(self.order, Decimal('1000'))
        adjust_customer_balance_for_order(self.order, -Decimal('1000'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('0'))

    def test_update_payment_status_unpaid(self):
        update_order_payment_status(self.order)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'unpaid')

    def test_update_payment_status_partial(self):
        OrderPayment.objects.create(order=self.order, amount=Decimal('300'), created_by=self.user)
        update_order_payment_status(self.order)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'partial')

    def test_update_payment_status_paid(self):
        OrderPayment.objects.create(order=self.order, amount=Decimal('1000'), created_by=self.user)
        update_order_payment_status(self.order)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')

    def test_update_payment_status_calculates_due(self):
        OrderPayment.objects.create(order=self.order, amount=Decimal('400'), created_by=self.user)
        update_order_payment_status(self.order)
        self.order.refresh_from_db()
        self.assertEqual(self.order.paid_amount, Decimal('400'))
        self.assertEqual(self.order.due_amount, Decimal('600'))
