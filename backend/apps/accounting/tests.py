from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Account, JournalEntry, JournalLine

User = get_user_model()


class AccountingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='accuser', password='testpass')
        self.revenue = Account.objects.create(
            code='4101',
            name_ar='ايرانات الطباعة',
            account_type='income',
        )
        self.cash = Account.objects.create(
            code='1101',
            name_ar='النقدية',
            account_type='asset',
        )
        self.expense = Account.objects.create(
            code='5101',
            name_ar='تكلفة الخامات',
            account_type='expense',
        )

    def test_create_journal_entry(self):
        entry = JournalEntry.objects.create(
            entry_date=timezone.now().date(),
            description='Test entry',
            created_by=self.user,
            status='posted',
            posted_at=timezone.now(),
        )
        self.assertIsNotNone(entry.entry_number)
        self.assertTrue(entry.entry_number.startswith('JE-'))

    def test_journal_entry_number_auto_generated(self):
        e1 = JournalEntry.objects.create(entry_date=timezone.now().date(), description='E1', created_by=self.user)
        e2 = JournalEntry.objects.create(entry_date=timezone.now().date(), description='E2', created_by=self.user)
        self.assertNotEqual(e1.entry_number, e2.entry_number)
        self.assertTrue(e2.entry_number > e1.entry_number)

    def test_balanced_entry(self):
        entry = JournalEntry.objects.create(entry_date=timezone.now().date(), description='Balanced', created_by=self.user)
        JournalLine.objects.create(entry=entry, account=self.cash, debit=Decimal('1000'))
        JournalLine.objects.create(entry=entry, account=self.revenue, credit=Decimal('1000'))
        self.assertTrue(entry.is_balanced())
        self.assertEqual(entry.total_debit(), Decimal('1000'))
        self.assertEqual(entry.total_credit(), Decimal('1000'))

    def test_unbalanced_entry(self):
        entry = JournalEntry.objects.create(entry_date=timezone.now().date(), description='Unbalanced', created_by=self.user)
        JournalLine.objects.create(entry=entry, account=self.cash, debit=Decimal('1000'))
        JournalLine.objects.create(entry=entry, account=self.revenue, credit=Decimal('500'))
        self.assertFalse(entry.is_balanced())
        self.assertNotEqual(entry.total_debit(), entry.total_credit())

    def test_multiple_lines(self):
        entry = JournalEntry.objects.create(entry_date=timezone.now().date(), description='Multi', created_by=self.user)
        JournalLine.objects.create(entry=entry, account=self.cash, debit=Decimal('1500'))
        JournalLine.objects.create(entry=entry, account=self.revenue, credit=Decimal('1000'))
        JournalLine.objects.create(entry=entry, account=self.expense, credit=Decimal('500'))
        self.assertTrue(entry.is_balanced())

    def test_entry_date_defaults_to_today(self):
        entry = JournalEntry.objects.create(description='Date test', created_by=self.user)
        self.assertEqual(entry.entry_date, timezone.now().date())

    def test_journal_line_creation(self):
        entry = JournalEntry.objects.create(entry_date=timezone.now().date(), description='Line test', created_by=self.user)
        line = JournalLine.objects.create(
            entry=entry,
            account=self.cash,
            debit=Decimal('500'),
            credit=Decimal('0'),
            description='Test line',
        )
        self.assertEqual(line.debit, Decimal('500'))
        self.assertEqual(line.credit, Decimal('0'))
        self.assertEqual(str(line.account), str(self.cash))
