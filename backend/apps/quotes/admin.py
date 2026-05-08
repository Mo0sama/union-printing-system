from django.contrib import admin

from .models import Quote, QuoteItem


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 1
    min_num = 1


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = [
        'quote_number', 'customer', 'quote_date', 'valid_until',
        'status', 'total', 'created_by'
    ]
    list_filter = ['status', 'quote_date', 'valid_until']
    search_fields = ['quote_number', 'customer__name', 'customer__company_name', 'customer__contact_person']
    readonly_fields = [
        'quote_number', 'quote_date', 'subtotal', 'tax_amount',
        'total', 'created_at', 'updated_at'
    ]
    inlines = [QuoteItemInline]
    date_hierarchy = 'quote_date'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
