from django.core.management.base import BaseCommand

from apps.orders.models import Order


class Command(BaseCommand):
    help = 'Recalculate totals and payment status for all existing orders'

    def handle(self, *args, **options):
        orders = Order.objects.prefetch_related('items', 'payments').all()
        fixed = 0
        for order in orders:
            if order.items.exists():
                order.calculate_totals()
                order.update_payment_status()
                fixed += 1
                self.stdout.write(f'  Fixed {order.order_number}: total={order.total}, paid={order.paid_amount}, due={order.due_amount}, status={order.payment_status}')
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed} orders'))
