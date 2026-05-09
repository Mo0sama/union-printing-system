from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.customers.models import Customer
from apps.employees.models import Employee

from .models import POSSession
from .services import adjust_customer_balance

User = get_user_model()


class POSBalanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='posuser', password='testpass')
        self.employee = Employee.objects.create(
            employee_code='EMP-TEST-001',
            full_name='Test Cashier',
            phone='01000000003',
            position='cashier',
            department='sales',
            base_salary=Decimal('5000'),
            hire_date=timezone.now().date(),
        )
        self.customer = Customer.objects.create(
            name='POS Customer', phone='01000000001', created_by=self.user
        )
        self.session = POSSession.objects.create(
            cashier=self.employee,
            opened_at=timezone.now(),
            status='open',
        )

    def test_sale_with_customer_increases_balance(self):
        adjust_customer_balance(self.customer, Decimal('500'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('500'))

    def test_sale_without_customer_does_not_crash(self):
        # Should not raise
        adjust_customer_balance(self.customer, Decimal('0'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('0'))

    def test_refund_decreases_balance(self):
        adjust_customer_balance(self.customer, Decimal('500'))
        adjust_customer_balance(self.customer, -Decimal('500'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('0'))

    def test_multiple_sales_accumulate(self):
        adjust_customer_balance(self.customer, Decimal('100'))
        adjust_customer_balance(self.customer, Decimal('200'))
        adjust_customer_balance(self.customer, Decimal('300'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('600'))
