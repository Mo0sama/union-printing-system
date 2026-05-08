from django.contrib import admin

from .models import DeliveryNote, DesignFile, Order, OrderItem, OrderPayment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    min_num = 1


class OrderPaymentInline(admin.TabularInline):
    model = OrderPayment
    extra = 0
    readonly_fields = ['created_by', 'created_at']


class DesignFileInline(admin.TabularInline):
    model = DesignFile
    extra = 0
    readonly_fields = ['uploaded_by', 'uploaded_at']


class DeliveryNoteInline(admin.TabularInline):
    model = DeliveryNote
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer', 'order_date', 'delivery_date',
        'status', 'priority', 'total', 'paid_amount', 'due_amount',
        'payment_status'
    ]
    list_filter = [
        'status', 'priority', 'payment_status', 'order_type',
        'order_date', 'delivery_date'
    ]
    search_fields = [
        'order_number', 'customer__name',
        'customer__company_name', 'customer__contact_person'
    ]
    readonly_fields = [
        'order_number', 'order_date', 'subtotal', 'tax_amount',
        'total', 'paid_amount', 'due_amount', 'payment_status',
        'created_at', 'updated_at'
    ]
    inlines = [OrderItemInline, OrderPaymentInline, DesignFileInline, DeliveryNoteInline]
    date_hierarchy = 'order_date'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'order', 'item_type', 'quantity', 'unit', 'total', 'status']
    list_filter = ['item_type', 'status']
    search_fields = ['description', 'order__order_number']


@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'payment_date', 'payment_method', 'reference']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['order__order_number']


@admin.register(DesignFile)
class DesignFileAdmin(admin.ModelAdmin):
    list_display = ['order', 'version', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at']


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(admin.ModelAdmin):
    list_display = ['order', 'delivered_by', 'received_by', 'delivery_date', 'status']
    list_filter = ['status', 'delivery_date']
