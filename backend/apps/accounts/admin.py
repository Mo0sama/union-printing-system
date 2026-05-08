from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'get_full_name', 'role',
        'phone', 'is_active', 'language_preference', 'date_joined'
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'language_preference')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('معلومات شخصية'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'role')
        }),
        (_('الصلاحيات'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('إعدادات'), {
            'fields': ('language_preference', 'employee_id'),
        }),
        (_('تواريخ مهمة'), {
            'fields': ('last_login', 'date_joined'),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'first_name', 'last_name', 'phone', 'role',
            ),
        }),
    )
