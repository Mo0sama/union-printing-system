from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.accounting.models import Account, JournalEntry, JournalLine
from apps.accounting.services import post_cogs, post_order_revenue
from apps.customers.models import Customer
from apps.inventory.models import Batch, Material
from apps.inventory.models import Category as InvCategory
from apps.inventory.services import deduct_stock_fifo
from apps.orders.models import Order, OrderItem, OrderPayment
from apps.orders.services import (
    adjust_customer_balance_for_order,
    adjust_customer_balance_for_payment,
    update_order_payment_status,
)

User = get_user_model()


class FullOrderFlowIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='admin123')
        self.customer = Customer.objects.create(
            name='Integration Customer', phone='01099999999', created_by=self.user
        )
        # Create inventory
        cat = InvCategory.objects.create(name='Paper', name_ar='ورق')
        self.material = Material.objects.create(
            name='A4 Paper', name_ar='ورق A4',
            category=cat, unit='piece',
            purchase_price=Decimal('0.5'), selling_price=Decimal('1'),
        )
        Batch.objects.create(
            batch_number='INT-BATCH-001',
            material=self.material,
            quantity=Decimal('1000'),
            remaining_quantity=Decimal('1000'),
            unit_price=Decimal('0.5'),
            purchase_date=timezone.now().date(),
        )
        # Initialize current_stock to match batch totals
        Material.objects.filter(pk=self.material.pk).update(current_stock=Decimal('1000'))
        self.material.refresh_from_db()
        # Create COA accounts needed for posting (codes match service lookups)
        Account.objects.create(code='41', name_ar='إيرادات', account_type='income')
        Account.objects.create(code='51', name_ar='تكلفة البضاعة المباعة', account_type='expense')
        Account.objects.create(code='1101', name_ar='النقدية', account_type='asset')
        Account.objects.create(code='1104', name_ar='عملاء', account_type='asset')
        Account.objects.create(code='1105', name_ar='المخزون', account_type='asset')
        Account.objects.create(code='2104', name_ar='ضريبة المبيعات', account_type='liability')

    def test_full_cycle_create_payment_revenue(self):
        # 1. Create order
        order = Order.objects.create(
            customer=self.customer,
            delivery_date=timezone.now().date() + timezone.timedelta(days=7),
            subtotal=Decimal('1000'),
            total=Decimal('1000'),
            paid_amount=Decimal('0'),
            due_amount=Decimal('1000'),
            created_by=self.user,
        )
        adjust_customer_balance_for_order(order, order.total)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('1000'))

        # 2. Add payment
        payment = OrderPayment.objects.create(
            order=order, amount=Decimal('400'),
            payment_date=timezone.now().date(),
            created_by=self.user,
        )
        adjust_customer_balance_for_payment(payment)
        update_order_payment_status(order)
        order.refresh_from_db()
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('600'))
        self.assertEqual(order.paid_amount, Decimal('400'))
        self.assertEqual(order.payment_status, 'partial')

        # 3. Pay remaining
        payment2 = OrderPayment.objects.create(
            order=order, amount=Decimal('600'),
            payment_date=timezone.now().date(),
            created_by=self.user,
        )
        adjust_customer_balance_for_payment(payment2)
        update_order_payment_status(order)
        order.refresh_from_db()
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('0'))
        self.assertEqual(order.payment_status, 'paid')

    def test_inventory_deduction_and_accounting(self):
        order = Order.objects.create(
            customer=self.customer,
            delivery_date=timezone.now().date() + timezone.timedelta(days=7),
            subtotal=Decimal('500'),
            total=Decimal('500'),
            created_by=self.user,
        )
        OrderItem.objects.create(
            order=order,
            description='A4 Paper x500',
            quantity=500,
            unit_price=Decimal('1'),
            total=Decimal('500'),
            material=self.material,
        )
        # Deduct stock
        deduct_stock_fifo(self.material, 500, reference_type='order', reference_id=order.pk, user=self.user)
        self.material.refresh_from_db()
        self.assertEqual(self.material.current_stock, Decimal('500'))

        # Post COGS
        post_cogs('order', order.pk, user=self.user)
        cogs_lines = JournalLine.objects.filter(account__account_type='expense')
        self.assertTrue(cogs_lines.exists())

        # Post revenue
        post_order_revenue(order, user=self.user)
        revenue_lines = JournalLine.objects.filter(account__account_type='income')
        self.assertTrue(revenue_lines.exists())

        # Verify journal entries created
        entries = JournalEntry.objects.all()
        self.assertTrue(entries.count() >= 2)

    def test_cancel_order_reverses_everything(self):
        order = Order.objects.create(
            customer=self.customer,
            delivery_date=timezone.now().date() + timezone.timedelta(days=7),
            order_date=timezone.now().date(),
            subtotal=Decimal('200'),
            total=Decimal('200'),
            created_by=self.user,
        )
        adjust_customer_balance_for_order(order, order.total)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('200'))

        # Cancel = reverse balance
        adjust_customer_balance_for_order(order, -order.total)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('0'))
