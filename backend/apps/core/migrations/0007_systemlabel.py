from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_notification'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemLabel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=200, unique=True, verbose_name='المفتاح')),
                ('value_ar', models.TextField(blank=True, verbose_name='النص (عربي)')),
                ('app_label', models.CharField(blank=True, db_index=True, max_length=50, verbose_name='التطبيق')),
                ('description', models.TextField(blank=True, verbose_name='الوصف')),
                ('is_active', models.BooleanField(default=True, verbose_name='مفعل')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'تسمية النظام',
                'verbose_name_plural': 'تسميات النظام',
                'ordering': ['app_label', 'key'],
            },
        ),
    ]
