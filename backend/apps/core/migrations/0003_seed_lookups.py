from django.db import migrations


def seed_lookups(apps, schema_editor):
    Lookup = apps.get_model('core', 'Lookup')
    lookups = []

    # Material Units
    for code, name_ar in [('piece', 'قطعة'), ('meter', 'متر'), ('sqm', 'متر مربع'),
                           ('roll', 'رول'), ('kg', 'كجم'), ('liter', 'لتر'), ('box', 'كرتونة')]:
        lookups.append(Lookup(type='material_unit', code=code, name=code, name_ar=name_ar, sort_order=len(lookups)))

    # Payment Methods
    for code, name_ar in [('cash', 'نقدي'), ('credit', 'آجل'), ('bank_transfer', 'تحويل بنكي'),
                           ('check', 'شيك'), ('installment', 'تقسيط')]:
        lookups.append(Lookup(type='payment_method', code=code, name=code, name_ar=name_ar, sort_order=len(lookups)))

    # Order Types
    for code, name_ar in [('normal', 'عادي'), ('urgent', 'عاجل'), ('sample', 'عينة'), ('maintenance', 'صيانة')]:
        lookups.append(Lookup(type='order_type', code=code, name=code, name_ar=name_ar, sort_order=len(lookups)))

    # Machine Types
    for code, name_ar in [('large_format', 'Large Format'), ('offset', 'Offset'), ('uv', 'UV'),
                           ('sublimation', 'Sublimation'), ('laser', 'Laser'),
                           ('finishing', 'Finishing'), ('other', 'Other')]:
        lookups.append(Lookup(type='machine_type', code=code, name=code, name_ar=name_ar, sort_order=len(lookups)))

    # Employee Departments
    for code, name_ar in [('management', 'إدارة'), ('design', 'تصميم'), ('printing', 'طباعة'),
                           ('finishing', 'تشطيب'), ('sales', 'مبيعات'),
                           ('warehouse', 'مخزن'), ('delivery', 'توصيل')]:
        lookups.append(Lookup(type='employee_dept', code=code, name=code, name_ar=name_ar, sort_order=len(lookups)))

    # Supplier Types
    for code, name_ar in [('material', 'خامات'), ('service', 'خدمات'), ('maintenance', 'صيانة'),
                           ('transport', 'نقل'), ('other', 'أخرى')]:
        lookups.append(Lookup(type='supplier_type', code=code, name=code, name_ar=name_ar, sort_order=len(lookups)))

    # Customer Types
    for code, name_ar in [('individual', 'فرد'), ('company', 'شركة'), ('government', 'حكومي')]:
        lookups.append(Lookup(type='customer_type', code=code, name=code, name_ar=name_ar, sort_order=len(lookups)))

    # VAT
    lookups.append(Lookup(type='vat', code='standard', name='Standard', name_ar='ضريبة قياسية', sort_order=0, is_active=True))

    Lookup.objects.bulk_create(lookups)


def reverse_seed(apps, schema_editor):
    Lookup = apps.get_model('core', 'Lookup')
    Lookup.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_lookup'),
    ]

    operations = [
        migrations.RunPython(seed_lookups, reverse_seed),
    ]
