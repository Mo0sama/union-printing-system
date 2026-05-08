from django.contrib import admin

from .models import Batch, Category, Material, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_ar', 'name', 'parent']
    search_fields = ['name', 'name_ar']


class BatchInline(admin.TabularInline):
    model = Batch
    extra = 1


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_ar', 'name', 'category', 'unit', 'current_stock', 'minimum_stock', 'is_active']
    list_filter = ['category', 'unit', 'is_active']
    search_fields = ['code', 'name', 'name_ar']
    list_editable = ['current_stock', 'minimum_stock', 'is_active']
    inlines = [BatchInline]


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'material', 'supplier', 'quantity', 'remaining_quantity', 'unit_price', 'purchase_date']
    list_filter = ['purchase_date', 'supplier']
    search_fields = ['batch_number', 'material__name']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['material', 'movement_type', 'quantity', 'created_by', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['material__name', 'material__code']
    readonly_fields = ['created_at']
