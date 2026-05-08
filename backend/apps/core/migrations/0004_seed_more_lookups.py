from django.db import migrations


def seed_lookups(apps, schema_editor):
    Lookup = apps.get_model('core', 'Lookup')
    lookups = []

    def add(type_key, code, name_ar):
        lookups.append(Lookup(type=type_key, code=code, name=code, name_ar=name_ar, sort_order=len(lookups)))

    # Order Status
    for code, name_ar in [('pending', 'قيد الانتظار'), ('confirmed', 'مؤكد'), ('in_design', 'في التصميم'),
                           ('in_production', 'في الإنتاج'), ('in_finishing', 'في التشطيب'),
                           ('quality_check', 'فحص الجودة'), ('ready', 'جاهز'),
                           ('delivered', 'تم التسليم'), ('cancelled', 'ملغي')]:
        add('order_status', code, name_ar)

    # Order Priority
    for code, name_ar in [('low', 'منخفض'), ('normal', 'عادي'), ('high', 'عالي'), ('urgent', 'عاجل')]:
        add('order_priority', code, name_ar)

    # Order Item Type
    for code, name_ar in [('printing', 'طباعة'), ('laser', 'ليزر'), ('engraving', 'حفر'),
                           ('design', 'تصميم'), ('material', 'خامات'), ('other', 'أخرى')]:
        add('order_item_type', code, name_ar)

    # Order Item Status
    for code, name_ar in [('pending', 'قيد الانتظار'), ('in_design', 'في التصميم'),
                           ('in_production', 'في الإنتاج'), ('in_finishing', 'في التشطيب'),
                           ('completed', 'مكتمل')]:
        add('order_item_status', code, name_ar)

    # Unit (unified across OrderItem, QuoteItem, Material)
    for code, name_ar in [('piece', 'قطعة'), ('meter', 'متر'), ('sqm', 'متر مربع'),
                           ('roll', 'رول'), ('set', 'طقم'), ('hour', 'ساعة'),
                           ('kg', 'كجم'), ('liter', 'لتر'), ('box', 'كرتونة')]:
        add('unit', code, name_ar)

    # Discount Type
    for code, name_ar in [('percentage', 'نسبة مئوية'), ('fixed', 'قيمة ثابتة')]:
        add('discount_type', code, name_ar)

    # Delivery Note Status
    for code, name_ar in [('partial', 'تسليم جزئي'), ('full', 'تسليم كامل')]:
        add('delivery_note_status', code, name_ar)

    # Production Job Status
    for code, name_ar in [('pending', 'قيد الانتظار'), ('in_progress', 'قيد التنفيذ'),
                           ('completed', 'مكتمل'), ('quality_check', 'فحص جودة'),
                           ('rejected', 'مرفوض'), ('paused', 'متوقف')]:
        add('production_job_status', code, name_ar)

    # Production Stage Status
    for code, name_ar in [('pending', 'قيد الانتظار'), ('in_progress', 'قيد التنفيذ'),
                           ('completed', 'مكتمل'), ('skipped', 'تم التجاهل')]:
        add('production_stage_status', code, name_ar)

    # Quality Check Result
    for code, name_ar in [('passed', 'مقبول'), ('failed', 'مرفوض'), ('conditional', 'معلق بشروط')]:
        add('quality_check_result', code, name_ar)

    # Machine Status
    for code, name_ar in [('active', 'نشط'), ('maintenance', 'صيانة'), ('inactive', 'غير نشط')]:
        add('machine_status', code, name_ar)

    # Quote Status
    for code, name_ar in [('draft', 'مسودة'), ('sent', 'مرسل'), ('accepted', 'مقبول'),
                           ('rejected', 'مرفوض'), ('expired', 'منتهي'), ('converted', 'محول لطلب')]:
        add('quote_status', code, name_ar)

    # Stock Movement Type
    for code, name_ar in [('purchase_in', 'مشتريات (وارد)'), ('return_in', 'مرتجع (وارد)'),
                           ('sale_out', 'مبيعات (صادر)'), ('usage_out', 'استخدام (صادر)'),
                           ('damage_out', 'تالف (صادر)'), ('transfer_out', 'تحويل (صادر)'),
                           ('adjustment_out', 'تسوية (صادر)'), ('adjustment_in', 'تسوية (وارد)'),
                           ('production_out', 'إنتاج (صادر)')]:
        add('stock_movement_type', code, name_ar)

    # POS Session Status
    for code, name_ar in [('open', 'مفتوحة'), ('closed', 'مغلقة')]:
        add('pos_session_status', code, name_ar)

    # POS Sale Status
    for code, name_ar in [('completed', 'مكتملة'), ('refunded', 'مسترجعة'), ('voided', 'ملغاة')]:
        add('pos_sale_status', code, name_ar)

    # POS Item Type
    for code, name_ar in [('product', 'منتج'), ('service', 'خدمة'), ('material', 'خامة')]:
        add('pos_item_type', code, name_ar)

    # Purchase Order Status
    for code, name_ar in [('draft', 'مسودة'), ('sent', 'مرسل'), ('confirmed', 'مؤكد'),
                           ('received', 'مستلم'), ('cancelled', 'ملغي')]:
        add('purchase_order_status', code, name_ar)

    # Interaction Type
    for code, name_ar in [('call', 'اتصال هاتفي'), ('email', 'بريد إلكتروني'),
                           ('visit', 'زيارة'), ('whatsapp', 'واتساب'), ('other', 'أخرى')]:
        add('interaction_type', code, name_ar)

    # Customer Payment Method
    for code, name_ar in [('cash', 'نقدي'), ('bank_transfer', 'تحويل بنكي'),
                           ('cheque', 'شيك'), ('credit_card', 'بطاقة ائتمان'), ('other', 'أخرى')]:
        add('customer_payment_method', code, name_ar)

    # Leave Type
    for code, name_ar in [('annual', 'سنوية'), ('sick', 'مرضية'),
                           ('emergency', 'طارئة'), ('unpaid', 'بدون راتب')]:
        add('leave_type', code, name_ar)

    # Leave Status
    for code, name_ar in [('pending', 'قيد الانتظار'), ('approved', 'معتمدة'), ('rejected', 'مرفوضة')]:
        add('leave_status', code, name_ar)

    # Attendance Status
    for code, name_ar in [('present', 'حاضر'), ('absent', 'غائب'), ('late', 'متأخر'),
                           ('half_day', 'نصف يوم'), ('holiday', 'إجازة رسمية'), ('leave', 'إجازة')]:
        add('attendance_status', code, name_ar)

    # Employee Salary Type
    for code, name_ar in [('fixed', 'ثابت'), ('hourly', 'بالساعة'), ('commission_based', 'عمولة')]:
        add('employee_salary_type', code, name_ar)

    Lookup.objects.bulk_create(lookups)


def reverse_seed(apps, schema_editor):
    Lookup = apps.get_model('core', 'Lookup')
    new_types = [
        'order_status', 'order_priority', 'order_item_type', 'order_item_status',
        'unit', 'discount_type', 'delivery_note_status',
        'production_job_status', 'production_stage_status', 'quality_check_result',
        'machine_status', 'quote_status', 'stock_movement_type',
        'pos_session_status', 'pos_sale_status', 'pos_item_type',
        'purchase_order_status', 'interaction_type', 'customer_payment_method',
        'leave_type', 'leave_status', 'attendance_status', 'employee_salary_type',
    ]
    Lookup.objects.filter(type__in=new_types).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_seed_lookups'),
    ]

    operations = [
        migrations.RunPython(seed_lookups, reverse_seed),
    ]
