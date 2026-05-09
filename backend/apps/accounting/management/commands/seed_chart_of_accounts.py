from django.core.management.base import BaseCommand
from apps.accounting.models import Account


COA = [
    {
        'code': '1',
        'name': 'Assets',
        'name_ar': 'الأصول',
        'account_type': 'asset',
        'children': [
            {
                'code': '11',
                'name': 'Current Assets',
                'name_ar': 'الأصول المتداولة',
                'account_type': 'asset',
                'children': [
                    {'code': '1101', 'name': 'Cash on Hand', 'name_ar': 'النقدية بالصندوق', 'account_type': 'asset'},
                    {'code': '1102', 'name': 'Petty Cash', 'name_ar': 'صندوق المصروفات النثرية', 'account_type': 'asset'},
                    {'code': '1103', 'name': 'Bank Accounts', 'name_ar': 'الحسابات البنكية', 'account_type': 'asset'},
                    {'code': '1104', 'name': 'Accounts Receivable', 'name_ar': 'عملاء (مدينون)', 'account_type': 'asset'},
                    {'code': '1105', 'name': 'Raw Materials Inventory', 'name_ar': 'مخزن خامات', 'account_type': 'asset'},
                    {'code': '1106', 'name': 'WIP Inventory', 'name_ar': 'مخزن تحت التشغيل', 'account_type': 'asset'},
                    {'code': '1107', 'name': 'Finished Goods Inventory', 'name_ar': 'مخزن تام الصنع', 'account_type': 'asset'},
                    {'code': '1108', 'name': 'Advances to Suppliers', 'name_ar': 'عربون موردين', 'account_type': 'asset'},
                    {'code': '1109', 'name': 'Prepaid Expenses', 'name_ar': 'مصروفات مدفوعة مقدماً', 'account_type': 'asset'},
                ],
            },
            {
                'code': '12',
                'name': 'Fixed Assets',
                'name_ar': 'الأصول الثابتة',
                'account_type': 'asset',
                'children': [
                    {'code': '1201', 'name': 'Printing Machines', 'name_ar': 'ماكينات طباعة', 'account_type': 'asset'},
                    {'code': '1202', 'name': 'Office Equipment', 'name_ar': 'أثاث ومعدات مكتبية', 'account_type': 'asset'},
                    {'code': '1203', 'name': 'Vehicles', 'name_ar': 'وسائل النقل', 'account_type': 'asset'},
                    {'code': '1204', 'name': 'Computers & IT Equipment', 'name_ar': 'أجهزة حاسب آلي', 'account_type': 'asset'},
                    {'code': '1205', 'name': 'Accumulated Depreciation', 'name_ar': 'مجمع الإهلاك', 'account_type': 'asset'},
                ],
            },
        ],
    },
    {
        'code': '2',
        'name': 'Liabilities',
        'name_ar': 'الخصوم',
        'account_type': 'liability',
        'children': [
            {
                'code': '21',
                'name': 'Current Liabilities',
                'name_ar': 'الخصوم المتداولة',
                'account_type': 'liability',
                'children': [
                    {'code': '2101', 'name': 'Accounts Payable', 'name_ar': 'موردون (دائنون)', 'account_type': 'liability'},
                    {'code': '2102', 'name': 'Customer Deposits', 'name_ar': 'عربون عملاء', 'account_type': 'liability'},
                    {'code': '2103', 'name': 'Accrued Expenses', 'name_ar': 'مصروفات مستحقة', 'account_type': 'liability'},
                    {'code': '2104', 'name': 'Tax Payable', 'name_ar': 'ضريبة مستحقة', 'account_type': 'liability'},
                    {'code': '2105', 'name': 'Salaries Payable', 'name_ar': 'رواتب مستحقة', 'account_type': 'liability'},
                ],
            },
            {
                'code': '22',
                'name': 'Long-term Liabilities',
                'name_ar': 'الخصوم طويلة الأجل',
                'account_type': 'liability',
                'children': [
                    {'code': '2201', 'name': 'Bank Loans', 'name_ar': 'قروض بنكية', 'account_type': 'liability'},
                ],
            },
        ],
    },
    {
        'code': '3',
        'name': 'Equity',
        'name_ar': 'حقوق الملكية',
        'account_type': 'equity',
        'children': [
            {'code': '31', 'name': 'Owner Capital', 'name_ar': 'رأس المال', 'account_type': 'equity'},
            {'code': '32', 'name': 'Retained Earnings', 'name_ar': 'أرباح محتجزة', 'account_type': 'equity'},
            {'code': '33', 'name': 'Current Year Profit/Loss', 'name_ar': 'أرباح/خسائر العام', 'account_type': 'equity'},
        ],
    },
    {
        'code': '4',
        'name': 'Income',
        'name_ar': 'الإيرادات',
        'account_type': 'income',
        'children': [
            {'code': '41', 'name': 'Printing Revenue', 'name_ar': 'إيرادات الطباعة', 'account_type': 'income'},
            {'code': '42', 'name': 'Design Revenue', 'name_ar': 'إيرادات التصميم', 'account_type': 'income'},
            {'code': '43', 'name': 'POS Sales Revenue', 'name_ar': 'إيرادات مبيعات نقدية', 'account_type': 'income'},
            {'code': '44', 'name': 'Discount Allowed', 'name_ar': 'خصم مسموح به', 'account_type': 'income'},
        ],
    },
    {
        'code': '5',
        'name': 'Expenses',
        'name_ar': 'المصروفات',
        'account_type': 'expense',
        'children': [
            {'code': '51', 'name': 'COGS - Materials', 'name_ar': 'تكلفة البضاعة المباعة - خامات', 'account_type': 'expense'},
            {'code': '52', 'name': 'COGS - Direct Labor', 'name_ar': 'تكلفة البضاعة المباعة - أجور مباشرة', 'account_type': 'expense'},
            {'code': '53', 'name': 'COGS - Overhead', 'name_ar': 'تكلفة البضاعة المباعة - تكاليف غير مباشرة', 'account_type': 'expense'},
            {'code': '54', 'name': 'Salaries & Wages', 'name_ar': 'رواتب وأجور', 'account_type': 'expense'},
            {'code': '55', 'name': 'Rent', 'name_ar': 'إيجار', 'account_type': 'expense'},
            {'code': '56', 'name': 'Utilities', 'name_ar': 'مرافق (كهرباء - مياه)', 'account_type': 'expense'},
            {'code': '57', 'name': 'Maintenance', 'name_ar': 'صيانة', 'account_type': 'expense'},
            {'code': '58', 'name': 'Marketing & Advertising', 'name_ar': 'دعاية وإعلان', 'account_type': 'expense'},
            {'code': '59', 'name': 'Administrative Expenses', 'name_ar': 'مصروفات إدارية عمومية', 'account_type': 'expense'},
        ],
    },
]


def create_accounts(data, parent=None):
    for item in data:
        children = item.pop('children', [])
        account, _ = Account.objects.update_or_create(
            code=item['code'],
            defaults={**item, 'parent': parent},
        )
        if children:
            create_accounts(children, parent=account)


class Command(BaseCommand):
    help = 'Seeds the standard Chart of Accounts for a printing business'

    def handle(self, *args, **options):
        if Account.objects.exists():
            self.stdout.write(self.style.WARNING('Accounts already exist, updating...'))
        create_accounts(COA)
        count = Account.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Chart of Accounts seeded: {count} accounts'))
