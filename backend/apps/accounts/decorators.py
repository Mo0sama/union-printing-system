from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def app_permission_required(perm_codename, login_url=None):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(login_url or 'accounts:login')
            if not request.user.has_perm(f'accounts.{perm_codename}'):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and u.role in ('admin', 'manager'),
        login_url='accounts:login',
    )(view_func)
