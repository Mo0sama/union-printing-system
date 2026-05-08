from django.contrib import admin

from .models import Customer, CustomerContact, CustomerInteraction, CustomerPayment


class CustomerContactInline(admin.TabularInline):
    model = CustomerContact
    extra = 1


class CustomerInteractionInline(admin.TabularInline):
    model = CustomerInteraction
    extra = 0
    readonly_fields = ('created_at',)


class CustomerPaymentInline(admin.TabularInline):
    model = CustomerPayment
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'name', 'customer_type', 'phone',
        'city', 'current_balance', 'credit_limit', 'is_active'
    )
    list_filter = ('customer_type', 'is_active', 'city')
    search_fields = ('code', 'name', 'company_name', 'contact_person', 'phone', 'email')
    readonly_fields = ('code', 'current_balance', 'created_at', 'updated_at')
    inlines = [CustomerContactInline, CustomerInteractionInline, CustomerPaymentInline]


@admin.register(CustomerContact)
class CustomerContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'phone', 'email', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('name', 'phone', 'email', 'customer__code')


@admin.register(CustomerInteraction)
class CustomerInteractionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'interaction_type', 'summary', 'created_by', 'created_at')
    list_filter = ('interaction_type', 'created_at')
    search_fields = ('summary', 'customer__code', 'customer__name', 'customer__company_name')
    readonly_fields = ('created_at',)


@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'amount', 'payment_date', 'payment_method', 'reference', 'created_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('reference', 'customer__code', 'customer__name', 'customer__company_name')
    readonly_fields = ('created_at',)
