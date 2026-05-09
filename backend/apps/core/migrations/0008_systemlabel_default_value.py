from django.db import migrations, models


def populate_default_value(apps, schema_editor):
    SystemLabel = apps.get_model('core', 'SystemLabel')
    for label in SystemLabel.objects.all():
        if label.value_ar and not label.default_value:
            label.default_value = label.value_ar
            label.save(update_fields=['default_value'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_systemlabel'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemlabel',
            name='default_value',
            field=models.TextField(blank=True, verbose_name='القيمة الافتراضية'),
        ),
        migrations.RunPython(populate_default_value, migrations.RunPython.noop),
    ]
