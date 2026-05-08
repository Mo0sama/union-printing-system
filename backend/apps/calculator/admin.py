from django.contrib import admin

from .models import (
    CalculatorQuote, CalculatorQuoteItem, GiveawayCategory,
    GiveawayOption, GiveawayPricingTier, GiveawayProduct,
    PricingTier, ServiceCategory, ServiceProduct,
)


class PricingTierInline(admin.TabularInline):
    model = PricingTier
    extra = 2


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name', 'sort_order', 'is_active']
    list_editable = ['sort_order', 'is_active']
    search_fields = ['name', 'name_ar']


@admin.register(ServiceProduct)
class ServiceProductAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'name_ar']
    inlines = [PricingTierInline]


class GiveawayPricingTierInline(admin.TabularInline):
    model = GiveawayPricingTier
    extra = 2


class GiveawayOptionInline(admin.TabularInline):
    model = GiveawayOption
    extra = 1


@admin.register(GiveawayCategory)
class GiveawayCategoryAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name', 'sort_order', 'is_active']
    list_editable = ['sort_order', 'is_active']
    search_fields = ['name', 'name_ar']


@admin.register(GiveawayProduct)
class GiveawayProductAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'name_ar']
    inlines = [GiveawayOptionInline, GiveawayPricingTierInline]


class CalculatorQuoteItemInline(admin.TabularInline):
    model = CalculatorQuoteItem
    extra = 0
    readonly_fields = ['product_type', 'category_name', 'product_name', 'option_name', 'quantity', 'unit_price', 'line_total']


@admin.register(CalculatorQuote)
class CalculatorQuoteAdmin(admin.ModelAdmin):
    list_display = ['quote_number', 'contact_name', 'contact_email', 'quote_type', 'total', 'status', 'created_at']
    list_filter = ['status', 'quote_type', 'created_at']
    search_fields = ['quote_number', 'contact_name', 'contact_email', 'company']
    readonly_fields = ['quote_number', 'subtotal', 'discount_amount', 'tax_amount', 'total', 'created_at', 'updated_at']
    inlines = [CalculatorQuoteItemInline]
    actions = ['mark_approved', 'mark_rejected']

    def mark_approved(self, request, queryset):
        queryset.update(status=CalculatorQuote.Status.APPROVED)
    mark_approved.short_description = 'تحديد كمقبول'

    def mark_rejected(self, request, queryset):
        queryset.update(status=CalculatorQuote.Status.REJECTED)
    mark_rejected.short_description = 'تحديد كمرفوض'
