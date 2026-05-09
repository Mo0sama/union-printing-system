from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, F, Q

from apps.core.models import SystemLabel

EXCLUDED_APPS = {'admin', 'auth', 'contenttypes', 'sessions', 'axes'}


def superuser_required(view):
    return user_passes_test(lambda u: u.is_superuser)(view)


@superuser_required
def dashboard(request):
    total_labels = SystemLabel.objects.exclude(app_label__in=EXCLUDED_APPS).count()
    customized = SystemLabel.objects.filter(is_active=True).exclude(app_label__in=EXCLUDED_APPS).exclude(value_ar='').exclude(value_ar=F('default_value')).count()
    active_overrides = SystemLabel.objects.filter(is_active=True).exclude(app_label__in=EXCLUDED_APPS).exclude(value_ar='').exclude(value_ar=F('default_value'))
    apps_list = (
        SystemLabel.objects.exclude(app_label__in=EXCLUDED_APPS)
        .values('app_label')
        .annotate(total=Count('id'))
        .order_by('app_label')
    )
    recent = SystemLabel.objects.filter(is_active=True).exclude(value_ar='').exclude(value_ar=F('default_value')).order_by('-updated_at')[:10]

    return render(request, 'backoffice/dashboard.html', {
        'total_labels': total_labels,
        'active_overrides': active_overrides,
        'apps_list': apps_list,
        'recent': recent,
    })


@superuser_required
def label_list(request):
    app = request.GET.get('app', '')
    search = request.GET.get('q', '')
    show_all = request.GET.get('show_all', False)

    qs = SystemLabel.objects.exclude(app_label__in=EXCLUDED_APPS)
    if app:
        qs = qs.filter(app_label=app)
    if search:
        qs = qs.filter(Q(key__icontains=search) | Q(value_ar__icontains=search) | Q(description__icontains=search))
    if not show_all:
        qs = qs.filter(is_active=True)

    apps_list = (
        SystemLabel.objects.exclude(app_label__in=EXCLUDED_APPS)
        .values('app_label')
        .annotate(total=Count('id'))
        .order_by('app_label')
    )

    return render(request, 'backoffice/label_list.html', {
        'labels': qs,
        'apps_list': apps_list,
        'current_app': app,
        'search': search,
        'show_all': show_all,
    })


@superuser_required
def label_edit(request, key):
    label = get_object_or_404(SystemLabel, key=key)

    if request.method == 'POST':
        value_ar = request.POST.get('value_ar', '')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == '1'

        label.value_ar = value_ar
        label.description = description
        label.is_active = is_active
        label.save()

        messages.success(request, f'تم تحديث التسمية: {label.key}')
        return redirect('backoffice:label_list')

    return render(request, 'backoffice/label_form.html', {
        'label': label,
    })


@superuser_required
def label_reset(request, key):
    label = get_object_or_404(SystemLabel, key=key)
    label.value_ar = ''
    label.is_active = True
    label.save()
    messages.success(request, f'تم إعادة تعيين التسمية: {label.key}')
    return redirect('backoffice:label_list')


@superuser_required
def import_labels(request):
    from django.core.management import call_command
    from io import StringIO
    out = StringIO()
    call_command('import_system_labels', stdout=out)
    messages.success(request, out.getvalue())
    return redirect('backoffice:dashboard')
