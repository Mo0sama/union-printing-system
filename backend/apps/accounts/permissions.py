PERMISSION_GROUPS = {
    'dashboard': {
        'label': 'لوحة التحكم',
        'perms': [
            ('dashboard_view', 'عرض لوحة التحكم'),
        ],
    },
    'customers': {
        'label': 'العملاء',
        'perms': [
            ('customers_view', 'عرض العملاء'),
            ('customers_create', 'إضافة عملاء'),
            ('customers_edit', 'تعديل العملاء'),
            ('customers_delete', 'حذف العملاء'),
        ],
    },
    'quotes': {
        'label': 'عروض الأسعار',
        'perms': [
            ('quotes_view', 'عرض عروض الأسعار'),
            ('quotes_create', 'إضافة عروض أسعار'),
            ('quotes_edit', 'تعديل عروض الأسعار'),
            ('quotes_delete', 'حذف عروض الأسعار'),
            ('quotes_convert', 'تحويل عرض سعر لطلب'),
        ],
    },
    'orders': {
        'label': 'الطلبات',
        'perms': [
            ('orders_view', 'عرض الطلبات'),
            ('orders_create', 'إضافة طلبات'),
            ('orders_edit', 'تعديل الطلبات'),
            ('orders_delete', 'حذف الطلبات'),
            ('orders_change_status', 'تغيير حالة الطلب'),
            ('orders_manage_payments', 'إدارة المدفوعات'),
        ],
    },
    'pos': {
        'label': 'نقطة البيع',
        'perms': [
            ('pos_view', 'عرض نقطة البيع'),
            ('pos_create', 'إنشاء فواتير بيع'),
            ('pos_refund', 'إرجاع فواتير البيع'),
            ('pos_manage_sessions', 'إدارة جلسات البيع'),
        ],
    },
    'production': {
        'label': 'الإنتاج',
        'perms': [
            ('production_view', 'عرض الإنتاج'),
            ('production_create', 'إنشاء أوامر إنتاج'),
            ('production_edit', 'تعديل أوامر الإنتاج'),
            ('production_delete', 'حذف أوامر الإنتاج'),
            ('production_quality', 'فحص الجودة'),
        ],
    },
    'inventory': {
        'label': 'المخزون',
        'perms': [
            ('inventory_view', 'عرض المخزون'),
            ('inventory_create', 'إضافة خامات'),
            ('inventory_edit', 'تعديل الخامات'),
            ('inventory_delete', 'حذف الخامات'),
            ('inventory_manage_stock', 'إدارة حركة المخزون'),
        ],
    },
    'suppliers': {
        'label': 'الموردين',
        'perms': [
            ('suppliers_view', 'عرض الموردين'),
            ('suppliers_create', 'إضافة موردين'),
            ('suppliers_edit', 'تعديل الموردين'),
            ('suppliers_delete', 'حذف الموردين'),
        ],
    },
    'purchase_orders': {
        'label': 'أوامر الشراء',
        'perms': [
            ('purchase_orders_view', 'عرض أوامر الشراء'),
            ('purchase_orders_create', 'إنشاء أوامر الشراء'),
            ('purchase_orders_edit', 'تعديل أوامر الشراء'),
            ('purchase_orders_delete', 'حذف أوامر الشراء'),
            ('purchase_orders_receive', 'استلام أوامر الشراء'),
        ],
    },
    'employees': {
        'label': 'الموظفين',
        'perms': [
            ('employees_view', 'عرض الموظفين'),
            ('employees_create', 'إضافة موظفين'),
            ('employees_edit', 'تعديل الموظفين'),
            ('employees_delete', 'حذف الموظفين'),
        ],
    },
    'attendance': {
        'label': 'الحضور والانصراف',
        'perms': [
            ('attendance_view', 'عرض الحضور'),
            ('attendance_create', 'تسجيل الحضور'),
            ('attendance_edit', 'تعديل الحضور'),
            ('attendance_delete', 'حذف الحضور'),
        ],
    },
    'salaries': {
        'label': 'الرواتب',
        'perms': [
            ('salaries_view', 'عرض الرواتب'),
            ('salaries_create', 'إنشاء الرواتب'),
            ('salaries_edit', 'تعديل الرواتب'),
            ('salaries_delete', 'حذف الرواتب'),
            ('salaries_pay', 'دفع الرواتب'),
        ],
       },
    'reports': {
        'label': 'التقارير',
        'perms': [
            ('reports_view', 'عرض التقارير'),
        ],
    },
    'settings': {
        'label': 'الإعدادات',
        'perms': [
            ('settings_view', 'عرض الإعدادات'),
            ('settings_edit', 'تعديل الإعدادات'),
        ],
    },
    'advanced_settings': {
        'label': 'الإعدادات المتقدمة',
        'perms': [
            ('advanced_settings_view', 'عرض الإعدادات المتقدمة'),
            ('advanced_settings_edit', 'تعديل الإعدادات المتقدمة'),
        ],
    },
    'users': {
        'label': 'المستخدمين والصلاحيات',
        'perms': [
            ('users_view', 'عرض المستخدمين'),
            ('users_create', 'إضافة مستخدمين'),
            ('users_edit', 'تعديل المستخدمين'),
            ('users_delete', 'حذف المستخدمين'),
        ],
    },
}

ALL_PERM_CODENAMES = [
    codename
    for group in PERMISSION_GROUPS.values()
    for codename, _ in group['perms']
]

ROLE_PRESETS = {
    'admin': {
        'label': 'مدير النظام',
        'permissions': '__all__',
    },
    'manager': {
        'label': 'مدير',
        'permissions': [
            'dashboard_view',
            'customers_view', 'customers_create', 'customers_edit',
            'quotes_view', 'quotes_create', 'quotes_edit', 'quotes_convert',
            'orders_view', 'orders_create', 'orders_edit', 'orders_change_status', 'orders_manage_payments',
            'pos_view', 'pos_create', 'pos_manage_sessions',
            'production_view', 'production_create', 'production_edit', 'production_quality',
            'inventory_view', 'inventory_create', 'inventory_edit', 'inventory_manage_stock',
            'suppliers_view', 'suppliers_create', 'suppliers_edit',
            'purchase_orders_view', 'purchase_orders_create', 'purchase_orders_edit', 'purchase_orders_receive',
            'employees_view', 'employees_create', 'employees_edit',
            'attendance_view', 'attendance_create', 'attendance_edit',
            'salaries_view', 'salaries_create', 'salaries_edit', 'salaries_pay',
            'reports_view',
            'settings_view', 'settings_edit',
            'advanced_settings_view',
            'users_view',
        ],
    },
    'supervisor': {
        'label': 'مشرف',
        'permissions': [
            'dashboard_view',
            'customers_view', 'customers_create', 'customers_edit',
            'quotes_view', 'quotes_create', 'quotes_edit',
            'orders_view', 'orders_create', 'orders_edit', 'orders_change_status',
            'production_view', 'production_create', 'production_edit', 'production_quality',
            'inventory_view',
            'suppliers_view',
            'purchase_orders_view',
            'employees_view',
            'attendance_view', 'attendance_create',
            'reports_view',
        ],
    },
    'cashier': {
        'label': 'كاشير',
        'permissions': [
            'dashboard_view',
            'customers_view', 'customers_create',
            'orders_view',
            'pos_view', 'pos_create', 'pos_refund',
        ],
    },
    'staff': {
        'label': 'موظف',
        'permissions': [
            'dashboard_view',
            'customers_view',
            'orders_view',
            'production_view',
            'inventory_view',
            'attendance_view', 'attendance_create',
        ],
    },
}

PERM_APP_MAP = {}
for group_key, group_data in PERMISSION_GROUPS.items():
    for codename, _ in group_data['perms']:
        PERM_APP_MAP[codename] = group_key


def get_role_permissions(role):
    if role not in ROLE_PRESETS:
        return set()
    preset = ROLE_PRESETS[role]
    if preset['permissions'] == '__all__':
        return set(ALL_PERM_CODENAMES)
    return set(preset['permissions'])
