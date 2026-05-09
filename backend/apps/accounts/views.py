from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import (
    CustomPasswordChangeForm,
    LoginForm,
    ProfileEditForm,
    UserCreationForm,
)
from .models import User
from .permissions import ALL_PERM_CODENAMES, PERMISSION_GROUPS, ROLE_PRESETS


def login_view(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            lang = user.language_preference
            request.session['django_language'] = lang

            messages.success(request, _('تم تسجيل الدخول بنجاح. مرحباً بك!'))
            next_url = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
            return redirect(next_url)
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, _('تم تسجيل الخروج بنجاح.'))
    return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            request.session['django_language'] = user.language_preference
            messages.success(request, _('تم تحديث الملف الشخصي بنجاح.'))
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('تم تغيير كلمة المرور بنجاح.'))
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'password_change': True,
    })


def is_admin(user):
    return user.is_authenticated and user.role in ('admin', 'manager')


@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'accounts/user_list.html', {'users': users})


def _get_user_permissions():
    ct = ContentType.objects.get_for_model(User)
    return {
        p.codename: p
        for p in Permission.objects.filter(content_type=ct, codename__in=ALL_PERM_CODENAMES)
    }


@login_required
@user_passes_test(is_admin)
def user_create(request):
    perm_map = _get_user_permissions()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_staff = True
                user.save()

                selected = request.POST.getlist('permissions')
                perms_to_set = [perm_map[c] for c in selected if c in perm_map]
                user.user_permissions.set(perms_to_set)

            messages.success(request, _('تم إنشاء المستخدم بنجاح.'))
            return redirect('accounts:user_list')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': _('إنشاء مستخدم جديد'),
        'permission_groups': PERMISSION_GROUPS,
        'all_permissions': perm_map,
        'role_presets': ROLE_PRESETS,
        'selected_perms': set(),
    })


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    perm_map = _get_user_permissions()

    if request.method == 'POST':
        form = UserCreationForm(request.POST, instance=user)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.save()

                selected = request.POST.getlist('permissions')
                perms_to_set = [perm_map[c] for c in selected if c in perm_map]
                user.user_permissions.set(perms_to_set)

            messages.success(request, _('تم تحديث المستخدم بنجاح.'))
            return redirect('accounts:user_list')
    else:
        form = UserCreationForm(instance=user)

    selected = set(user.user_permissions.filter(
        codename__in=ALL_PERM_CODENAMES
    ).values_list('codename', flat=True))

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': _('تعديل المستخدم'),
        'edit_user': user,
        'permission_groups': PERMISSION_GROUPS,
        'all_permissions': perm_map,
        'role_presets': ROLE_PRESETS,
        'selected_perms': selected,
    })


@login_required
@user_passes_test(is_admin)
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_perms = user.user_permissions.filter(codename__in=ALL_PERM_CODENAMES).values_list('codename', flat=True)
    user_perm_set = set(user_perms)

    return render(request, 'accounts/user_detail.html', {
        'edit_user': user,
        'permission_groups': PERMISSION_GROUPS,
        'selected_perms': user_perm_set,
    })


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, _('تم حذف المستخدم "%s" بنجاح.') % username)
        return redirect('accounts:user_list')

    return render(request, 'accounts/user_confirm_delete.html', {
        'user': user,
    })
