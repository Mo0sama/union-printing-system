from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import User
from apps.accounts.permissions import ALL_PERM_CODENAMES


class Command(BaseCommand):
    help = 'Sync custom permission objects to database'

    def handle(self, *args, **options):
        ct, _ = ContentType.objects.get_or_create(
            app_label='accounts', model='user',
        )
        names = {
            'dashboard_view': 'Can view dashboard',
            'customers_view': 'Can view customers',
            'customers_create': 'Can create customers',
            'customers_edit': 'Can edit customers',
            'customers_delete': 'Can delete customers',
            'quotes_view': 'Can view quotes',
            'quotes_create': 'Can create quotes',
            'quotes_edit': 'Can edit quotes',
            'quotes_delete': 'Can delete quotes',
            'quotes_convert': 'Can convert quote to order',
            'orders_view': 'Can view orders',
            'orders_create': 'Can create orders',
            'orders_edit': 'Can edit orders',
            'orders_delete': 'Can delete orders',
            'orders_change_status': 'Can change order status',
            'orders_manage_payments': 'Can manage order payments',
            'pos_view': 'Can view POS',
            'pos_create': 'Can create POS sales',
            'pos_refund': 'Can refund POS sales',
            'pos_manage_sessions': 'Can manage POS sessions',
            'production_view': 'Can view production',
            'production_create': 'Can create production jobs',
            'production_edit': 'Can edit production jobs',
            'production_delete': 'Can delete production jobs',
            'production_quality': 'Can perform quality checks',
            'inventory_view': 'Can view inventory',
            'inventory_create': 'Can create materials',
            'inventory_edit': 'Can edit materials',
            'inventory_delete': 'Can delete materials',
            'inventory_manage_stock': 'Can manage stock movements',
            'suppliers_view': 'Can view suppliers',
            'suppliers_create': 'Can create suppliers',
            'suppliers_edit': 'Can edit suppliers',
            'suppliers_delete': 'Can delete suppliers',
            'purchase_orders_view': 'Can view purchase orders',
            'purchase_orders_create': 'Can create purchase orders',
            'purchase_orders_edit': 'Can edit purchase orders',
            'purchase_orders_delete': 'Can delete purchase orders',
            'purchase_orders_receive': 'Can receive purchase orders',
            'employees_view': 'Can view employees',
            'employees_create': 'Can create employees',
            'employees_edit': 'Can edit employees',
            'employees_delete': 'Can delete employees',
            'attendance_view': 'Can view attendance',
            'attendance_create': 'Can create attendance',
            'attendance_edit': 'Can edit attendance',
            'attendance_delete': 'Can delete attendance',
            'salaries_view': 'Can view salaries',
            'salaries_create': 'Can create salaries',
            'salaries_edit': 'Can edit salaries',
            'salaries_delete': 'Can delete salaries',
            'salaries_pay': 'Can pay salaries',
            'reports_view': 'Can view reports',
            'settings_view': 'Can view settings',
            'settings_edit': 'Can edit settings',
            'advanced_settings_view': 'Can view advanced settings',
            'advanced_settings_edit': 'Can edit advanced settings',
            'users_view': 'Can view users',
            'users_create': 'Can create users',
            'users_edit': 'Can edit users',
            'users_delete': 'Can delete users',
        }

        created = 0
        for codename in ALL_PERM_CODENAMES:
            perm, is_new = Permission.objects.get_or_create(
                content_type=ct,
                codename=codename,
                defaults={'name': names.get(codename, codename)},
            )
            if is_new:
                created += 1
                self.stdout.write(f'  Created permission: {codename}')

        self.stdout.write(self.style.SUCCESS(f'Sync complete. Created {created} new permissions.'))
