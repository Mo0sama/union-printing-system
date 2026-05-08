from django.contrib import admin
from .models import POSSession, POSSale, POSSaleItem


class POSSaleItemInline(admin.TabularInline):
    model = POSSaleItem
    extra = 1
    readonly_fields = ['total']


@admin.register(POSSession)
class POSSessionAdmin(admin.ModelAdmin):
    list_display = ['session_number', 'cashier', 'opened_at', 'closed_at',
                    'opening_balance', 'status']
    list_filter = ['status']
    search_fields = ['session_number', 'cashier__full_name']
    readonly_fields = ['session_number', 'opened_at']


@admin.register(POSSale)
class POSSaleAdmin(admin.ModelAdmin):
    list_display = ['sale_number', 'session', 'customer', 'sale_date',
                    'total', 'payment_method', 'status']
    list_filter = ['status', 'payment_method', 'sale_date']
    search_fields = ['sale_number', 'customer__name', 'customer__phone']
    readonly_fields = ['sale_number', 'sale_date', 'change_amount']
    inlines = [POSSaleItemInline]
