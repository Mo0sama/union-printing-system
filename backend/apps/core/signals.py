from django.db.models.signals import post_save
from django.dispatch import receiver

from .notifications import notify_low_stock, notify_order_created, notify_production_job_created


@receiver(post_save, sender='inventory.Material')
def check_low_stock(sender, instance, **kwargs):
    if instance.current_stock <= instance.minimum_stock and instance.minimum_stock > 0:
        notify_low_stock(instance)


@receiver(post_save, sender='orders.Order')
def order_created_notification(sender, instance, created, **kwargs):
    if created:
        notify_order_created(instance)


@receiver(post_save, sender='production.ProductionJob')
def production_job_created_notification(sender, instance, created, **kwargs):
    if created:
        notify_production_job_created(instance)
