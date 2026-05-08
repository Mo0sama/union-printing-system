from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Category, Material, Batch
from .services import deduct_stock_fifo, reverse_stock_deduction

User = get_user_model()


class InventoryServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='invuser', password='testpass')
        self.category = Category.objects.create(name='Test Cat', name_ar='تصنيف اختبار')
        self.material = Material.objects.create(
            name='Test Material',
            name_ar='خامة اختبار',
            category=self.category,
            unit='piece',
            purchase_price=Decimal('10'),
            selling_price=Decimal('15'),
        )
        # Create two batches with different costs for FIFO testing
        self.batch1 = Batch.objects.create(
            batch_number='BATCH-001',
            material=self.material,
            quantity=Decimal('100'),
            remaining_quantity=Decimal('100'),
            unit_price=Decimal('10'),
            purchase_date=timezone.now().date(),
        )
        self.batch2 = Batch.objects.create(
            batch_number='BATCH-002',
            material=self.material,
            quantity=Decimal('100'),
            remaining_quantity=Decimal('100'),
            unit_price=Decimal('12'),
            purchase_date=timezone.now().date(),
        )

    def test_initial_stock(self):
        self.material.refresh_from_db()
        self.assertEqual(self.material.current_stock, Decimal('200'))

    def test_deduct_stock_fifo_uses_oldest_batch_first(self):
        deduct_stock_fifo(self.material, Decimal('60'), reference_type='test', reference_id=1, user=self.user)
        self.batch1.refresh_from_db()
        self.batch2.refresh_from_db()
        self.assertEqual(self.batch1.remaining_quantity, Decimal('40'))
        self.assertEqual(self.batch2.remaining_quantity, Decimal('100'))

    def test_deduct_stock_fifo_crosses_batches(self):
        deduct_stock_fifo(self.material, Decimal('150'), reference_type='test', reference_id=2, user=self.user)
        self.batch1.refresh_from_db()
        self.batch2.refresh_from_db()
        self.assertEqual(self.batch1.remaining_quantity, Decimal('0'))
        self.assertEqual(self.batch2.remaining_quantity, Decimal('50'))

    def test_deduct_stock_fifo_entire_stock(self):
        deduct_stock_fifo(self.material, Decimal('200'), reference_type='test', reference_id=3, user=self.user)
        self.batch1.refresh_from_db()
        self.batch2.refresh_from_db()
        self.assertEqual(self.batch1.remaining_quantity, Decimal('0'))
        self.assertEqual(self.batch2.remaining_quantity, Decimal('0'))

    def test_deduct_updates_material_stock(self):
        deduct_stock_fifo(self.material, Decimal('30'), reference_type='test', reference_id=4, user=self.user)
        self.material.refresh_from_db()
        self.assertEqual(self.material.current_stock, Decimal('170'))

    def test_reverse_stock_deduction(self):
        deduct_stock_fifo(self.material, Decimal('50'), reference_type='test', reference_id=5, user=self.user)
        reverse_stock_deduction('test', 5, user=self.user)
        self.batch1.refresh_from_db()
        self.material.refresh_from_db()
        self.assertEqual(self.batch1.remaining_quantity, Decimal('100'))
        self.assertEqual(self.material.current_stock, Decimal('200'))
