from django.db import migrations


def assign_admin_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    User = apps.get_model('accounts', 'User')

    ct = ContentType.objects.get_for_model(User)
    admin_codenames = [
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

    perms = Permission.objects.filter(content_type=ct, codename__in=admin_codenames)
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.user_permissions.add(*perms)
    except User.DoesNotExist:
        pass


def remove_admin_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    User = apps.get_model('accounts', 'User')

    ct = ContentType.objects.get_for_model(User)
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.user_permissions.filter(content_type=ct).clear()
    except User.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_create_custom_permissions'),
    ]

    operations = [
        migrations.RunPython(assign_admin_permissions, remove_admin_permissions),
    ]
