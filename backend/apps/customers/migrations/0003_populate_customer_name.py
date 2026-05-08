from django.db import migrations


def populate_customer_name(apps, schema_editor):
    Customer = apps.get_model('customers', 'Customer')
    for customer in Customer.objects.all():
        if customer.customer_type == 'company' and customer.company_name:
            customer.name = customer.company_name
        elif customer.contact_person:
            customer.name = customer.contact_person
        else:
            customer.name = customer.phone
        customer.save(update_fields=['name'])


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_customer_name'),
    ]

    operations = [
        migrations.RunPython(populate_customer_name),
    ]
