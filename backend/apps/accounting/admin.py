from django.contrib import admin

from .models import Account, JournalEntry, JournalLine


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 1
    fields = ['account', 'debit', 'credit', 'description']


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name_ar', 'name', 'account_type', 'parent', 'is_active']
    list_filter = ['account_type', 'is_active']
    search_fields = ['code', 'name', 'name_ar']
    list_editable = ['is_active']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'entry_date', 'description', 'status', 'created_by', 'created_at']
    list_filter = ['status', 'entry_date']
    search_fields = ['entry_number', 'description']
    readonly_fields = ['created_at', 'posted_at']
    inlines = [JournalLineInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
