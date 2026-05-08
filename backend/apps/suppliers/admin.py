from django.contrib import admin

from .models import PurchaseOrder, PurchaseOrderItem, Supplier, SupplierPayment


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1


class SupplierPaymentInline(admin.TabularInline):
    model = SupplierPayment
    extra = 0


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'company_name', 'contact_person', 'phone', 'supply_type', 'current_balance', 'is_active']
    list_filter = ['is_active', 'supply_type']
    search_fields = ['code', 'company_name', 'contact_person', 'phone']
    inlines = [SupplierPaymentInline]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'order_date', 'status', 'total', 'paid_amount']
    list_filter = ['status', 'order_date']
    search_fields = ['po_number', 'supplier__company_name']
    inlines = [PurchaseOrderItemInline]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'material', 'quantity', 'unit_price', 'total', 'received_quantity']


@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'purchase_order', 'amount', 'payment_date', 'payment_method']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['supplier__company_name']
