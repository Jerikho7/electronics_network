from django.contrib import admin
from django.utils.html import format_html
from .models import NetworkNode, Product

@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "city",
        "country",
        "supplier_link",
        "debt",
        "created_at",
        "level_display",
    )
    list_filter = ("country", "city")
    search_fields = ("name", "city", "country", "email")
    readonly_fields = ("created_at",)
    actions = ["clear_debt"]

    def level_display(self, obj):
        return obj.level
    level_display.short_description = "Уровень"

    def supplier_link(self, obj):
        if not obj.supplier:
            return "—"
        url = f"/admin/network/networknode/{obj.supplier_id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.supplier)
    supplier_link.short_description = "Поставщик"

    @admin.action(description="Очистить задолженность у выбранных")
    def clear_debt(self, request, queryset):
        updated = queryset.update(debt=0)
        self.message_user(request, f"Обнулено задолженностей: {updated}")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "model", "release_date", "owner")
    list_filter = ("release_date", "owner__city", "owner__country")
    search_fields = ("title", "model", "owner__name")
