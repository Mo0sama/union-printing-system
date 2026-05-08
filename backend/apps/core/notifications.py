from .models import Notification


def create_notification(recipient, notification_type, title, message, link=''):
    Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )


def notify_admins(notification_type, title, message, link=''):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admins = User.objects.filter(role__in=['admin', 'manager'], is_active=True)
    for admin in admins:
        create_notification(admin, notification_type, title, message, link)


def notify_order_created(order):
    title = f'طلب جديد {order.order_number}'
    message = f'تم إنشاء طلب جديد بواسطة {order.customer} بقيمة {order.total}'
    link = f'/orders/orders/{order.pk}/'
    notify_admins('order', title, message, link)


def notify_order_status_changed(order, old_status, new_status):
    title = f'تحديث حالة الطلب {order.order_number}'
    message = f'تم تغيير حالة الطلب من {old_status} إلى {new_status}'
    link = f'/orders/orders/{order.pk}/'
    notify_admins('order', title, message, link)


def notify_payment_received(order, amount):
    title = f'دفعة مستلمة للطلب {order.order_number}'
    message = f'تم استلام دفعة بقيمة {amount} على الطلب {order.order_number}'
    link = f'/orders/orders/{order.pk}/'
    notify_admins('payment', title, message, link)


def notify_low_stock(material):
    title = f'تنبيه مخزون: {material.name}'
    message = f'المخزون من {material.name} منخفض ({material.current_stock})، الحد الأدنى: {material.minimum_stock}'
    link = f'/inventory/materials/{material.pk}/'
    notify_admins('inventory', title, message, link)


def notify_production_job_created(job):
    title = f'أمر إنتاج جديد {job.job_number}'
    message = f'تم إنشاء أمر إنتاج للطلب {job.order.order_number}'
    link = f'/production/jobs/{job.pk}/'
    notify_admins('production', title, message, link)
