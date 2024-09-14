from django.contrib import admin
from .models import Bill, BillItem


class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1
    readonly_fields = ["product", "quantity", "price"]


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "total_amount", "item_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "user__name"]
    readonly_fields = ["user", "total_amount", "created_at"]
    inlines = [BillItemInline]

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = "Number of Items"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ["bill", "product", "quantity", "price"]
    list_filter = ["bill__created_at"]
    search_fields = ["bill__user__email", "product__name"]
    readonly_fields = ["bill", "product", "quantity", "price"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
