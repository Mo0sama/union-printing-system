from django.contrib import admin

from .models import ActivityLog, CompanySetting, Lookup


@admin.register(CompanySetting)
class CompanySettingAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'currency', 'language', 'updated_at')
    exclude = ('pk',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'created_at')
    list_filter = ('action', 'model_name', 'created_at')
    search_fields = ('user__username', 'action', 'model_name', 'details')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'details', 'ip_address', 'created_at')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(Lookup)
class LookupAdmin(admin.ModelAdmin):
    list_display = ('type', 'code', 'name_ar', 'name', 'sort_order', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'name_ar', 'code')
    list_editable = ('sort_order', 'is_active')
