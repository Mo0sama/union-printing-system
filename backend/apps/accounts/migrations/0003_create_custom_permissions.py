from django.db import migrations


def create_custom_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    User = apps.get_model('accounts', 'User')

    ct, _ = ContentType.objects.get_or_create(
        app_label='accounts', model='user',
    )

    codenames = [
        'dashboard_view',
        'customers_view', 'customers_create', 'customers_edit', 'customers_delete',
        'quotes_view', 'quotes_create', 'quotes_edit', 'quotes_delete', 'quotes_convert',
        'orders_view', 'orders_create', 'orders_edit', 'orders_delete', 'orders_change_status', 'orders_manage_payments',
        'pos_view', 'pos_create', 'pos_refund', 'pos_manage_sessions',
        'production_view', 'production_create', 'production_edit', 'production_delete', 'production_quality',
        'inventory_view', 'inventory_create', 'inventory_edit', 'inventory_delete', 'inventory_manage_stock',
        'suppliers_view', 'suppliers_create', 'suppliers_edit', 'suppliers_delete',
        'purchase_orders_view', 'purchase_orders_create', 'purchase_orders_edit', 'purchase_orders_delete', 'purchase_orders_receive',
        'employees_view', 'employees_create', 'employees_edit', 'employees_delete',
        'attendance_view', 'attendance_create', 'attendance_edit', 'attendance_delete',
        'salaries_view', 'salaries_create', 'salaries_edit', 'salaries_delete', 'salaries_pay',
        'reports_view',
        'settings_view', 'settings_edit',
        'advanced_settings_view', 'advanced_settings_edit',
        'users_view', 'users_create', 'users_edit', 'users_delete',
    ]

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

    for codename in codenames:
        Permission.objects.get_or_create(
            content_type=ct,
            codename=codename,
            defaults={'name': names.get(codename, codename)},
        )


def remove_custom_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    ct = ContentType.objects.filter(
        app_label='accounts', model='user',
    ).first()
    if ct:
        codenames = [
            'dashboard_view',
            'customers_view', 'customers_create', 'customers_edit', 'customers_delete',
            'quotes_view', 'quotes_create', 'quotes_edit', 'quotes_delete', 'quotes_convert',
            'orders_view', 'orders_create', 'orders_edit', 'orders_delete', 'orders_change_status', 'orders_manage_payments',
            'pos_view', 'pos_create', 'pos_refund', 'pos_manage_sessions',
            'production_view', 'production_create', 'production_edit', 'production_delete', 'production_quality',
            'inventory_view', 'inventory_create', 'inventory_edit', 'inventory_delete', 'inventory_manage_stock',
            'suppliers_view', 'suppliers_create', 'suppliers_edit', 'suppliers_delete',
            'purchase_orders_view', 'purchase_orders_create', 'purchase_orders_edit', 'purchase_orders_delete', 'purchase_orders_receive',
            'employees_view', 'employees_create', 'employees_edit', 'employees_delete',
            'attendance_view', 'attendance_create', 'attendance_edit', 'attendance_delete',
            'salaries_view', 'salaries_create', 'salaries_edit', 'salaries_delete', 'salaries_pay',
            'reports_view',
            'settings_view', 'settings_edit',
            'advanced_settings_view', 'advanced_settings_edit',
            'users_view', 'users_create', 'users_edit', 'users_delete',
        ]
        Permission.objects.filter(
            content_type=ct,
            codename__in=codenames,
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(create_custom_permissions, remove_custom_permissions),
    ]
