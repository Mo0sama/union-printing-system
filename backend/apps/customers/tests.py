from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Customer
from .services import adjust_balance, record_customer_payment

User = get_user_model()


class CustomerBalanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='custuser', password='testpass')
        self.customer = Customer.objects.create(
            name='Balance Customer', phone='01000000002', created_by=self.user
        )

    def test_initial_balance_zero(self):
        self.assertEqual(self.customer.current_balance, Decimal('0'))

    def test_adjust_balance_positive(self):
        adjust_balance(self.customer, Decimal('500'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('500'))

    def test_adjust_balance_negative(self):
        adjust_balance(self.customer, Decimal('500'))
        adjust_balance(self.customer, -Decimal('200'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('300'))

    def test_get_balance_display_positive(self):
        self.customer.current_balance = Decimal('100')
        self.customer.save()
        self.assertIn('100', self.customer.get_balance_display())
        self.assertIn('مدين', self.customer.get_balance_display())

    def test_get_balance_display_negative(self):
        self.customer.current_balance = Decimal('-50')
        self.customer.save()
        self.assertIn('50', self.customer.get_balance_display())
        self.assertIn('دائن', self.customer.get_balance_display())

    def test_get_balance_display_zero(self):
        self.customer.current_balance = Decimal('0')
        self.customer.save()
        self.assertEqual(self.customer.get_balance_display(), 'صفر')

    def test_record_payment_decreases_balance(self):
        adjust_balance(self.customer, Decimal('1000'))
        record_customer_payment(
            customer=self.customer,
            amount=Decimal('400'),
            payment_date=timezone.now().date(),
            payment_method='cash',
            reference='',
            notes='',
            user=self.user,
        )
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('600'))

    def test_record_payment_creates_payment_record(self):
        adjust_balance(self.customer, Decimal('500'))
        payment = record_customer_payment(
            customer=self.customer,
            amount=Decimal('200'),
            payment_date=timezone.now().date(),
            payment_method='bank',
            reference='REF001',
            notes='test payment',
            user=self.user,
        )
        self.assertEqual(payment.amount, Decimal('200'))
        self.assertEqual(payment.payment_method, 'bank')
        self.assertEqual(payment.reference, 'REF001')
