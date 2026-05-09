from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models

from apps.core.models import SystemLabel


def set_label(key, value_ar, app_label, description=""):
    if not value_ar:
        return
    obj, created = SystemLabel.objects.get_or_create(
        key=key,
        defaults=dict(
            value_ar=value_ar,
            default_value=value_ar,
            app_label=app_label,
            description=description,
            is_active=True,
        ),
    )
    if not created:
        changed = False
        if obj.default_value != value_ar:
            obj.default_value = value_ar
            changed = True
        if obj.app_label != app_label:
            obj.app_label = app_label
            changed = True
        if obj.description != description:
            obj.description = description
            changed = True
        if changed:
            obj.save(update_fields=['default_value', 'app_label', 'description'])


class Command(BaseCommand):
    help = "Scan all models and create SystemLabel entries for every text in the system"

    def handle(self, *args, **options):
        count = 0

        for app_config in apps.get_app_configs():
            app_label = app_config.label
            if app_label.startswith("django"):
                continue

            for model in app_config.get_models():
                meta = model._meta

                # Model verbose_name
                key = f"{app_label}.{model.__name__}.verbose_name"
                set_label(key, str(meta.verbose_name or ""), app_label,
                          f"اسم نموذج {meta.verbose_name}")
                count += 1

                # Model verbose_name_plural
                key = f"{app_label}.{model.__name__}.verbose_name_plural"
                set_label(key, str(meta.verbose_name_plural or ""), app_label,
                          f"اسم النموذج (جمع) {meta.verbose_name_plural}")
                count += 1

                # Field labels
                for field in meta.fields:
                    if hasattr(field, 'verbose_name') and field.verbose_name:
                        fname = field.verbose_name
                        if isinstance(fname, str) and fname[0].isupper():
                            continue
                        key = f"{app_label}.{model.__name__}.{field.name}.verbose_name"
                        set_label(key, str(fname), app_label,
                                  f"حقل {fname} في {meta.verbose_name}")
                        count += 1

                # Choices / TextChoices
                for field in meta.fields:
                    if hasattr(field, 'choices') and field.choices:
                        for value, label in field.choices:
                            key = f"{app_label}.{model.__name__}.{field.name}.choices.{value}"
                            set_label(key, str(label), app_label,
                                      f"خيار {label} في حقل {field.verbose_name}")
                            count += 1

                # ForeignKey related names
                for rel in meta.related_objects:
                    if rel.related_name:
                        rn = rel.related_name
                        if callable(rn):
                            continue
                        key = f"{app_label}.{model.__name__}.related.{rn}"
                        set_label(key, str(rn), app_label,
                                  f"علاقة {rn} في {meta.verbose_name}")

        # Notification types
        notif_types = [
            ('order', 'طلب'), ('production', 'إنتاج'), ('payment', 'دفعة'),
            ('inventory', 'مخزون'), ('quote', 'عرض سعر'), ('system', 'النظام'),
        ]
        for value, label in notif_types:
            key = f"core.Notification.notification_type.choices.{value}"
            set_label(key, label, "core", f"نوع الإشعار: {label}")
            count += 1

        # Lookup Type labels
        for choice in models.TextChoices.__subclasses__():
            for member in choice:
                key = f"core.Lookup.type.choices.{member.value}"
                set_label(key, str(member.label), "core",
                          f"نوع lookup: {member.label}")
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {count} system labels"))
