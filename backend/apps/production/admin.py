from django.contrib import admin

from .models import Department, Machine, ProductionJob, ProductionStage, QualityCheck


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_ar', 'name', 'sort_order']
    search_fields = ['name', 'name_ar', 'code']
    list_editable = ['sort_order']


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ['name', 'machine_type', 'department', 'status']
    list_filter = ['machine_type', 'department', 'status']
    search_fields = ['name', 'serial_number']


class ProductionStageInline(admin.TabularInline):
    model = ProductionStage
    extra = 1


class QualityCheckInline(admin.TabularInline):
    model = QualityCheck
    extra = 0


@admin.register(ProductionJob)
class ProductionJobAdmin(admin.ModelAdmin):
    list_display = ['job_number', 'order', 'department', 'status', 'priority', 'assigned_to', 'created_at']
    list_filter = ['status', 'priority', 'department', 'machine']
    search_fields = ['job_number', 'order__order_number']
    inlines = [ProductionStageInline, QualityCheckInline]
    readonly_fields = ['job_number', 'created_at', 'updated_at']


@admin.register(ProductionStage)
class ProductionStageAdmin(admin.ModelAdmin):
    list_display = ['production_job', 'stage_name', 'stage_order', 'status']
    list_filter = ['status']


@admin.register(QualityCheck)
class QualityCheckAdmin(admin.ModelAdmin):
    list_display = ['production_job', 'checked_by', 'check_date', 'result']
    list_filter = ['result']
