def lookup_choices(lookup_type):
    from .models import Lookup
    return [(l.code, l.name_ar) for l in Lookup.objects.filter(type=lookup_type, is_active=True).order_by('sort_order')]


def set_lookup_choices(form, field_name, lookup_type):
    if field_name in form.fields:
        form.fields[field_name].choices = lookup_choices(lookup_type)
