from django.contrib import admin

from network.models import NetworkNode, Product


@admin.register(NetworkNode)
class NetworkNodeAdmin(admin.ModelAdmin):
    def get_level(self, obj):
        return obj.level

    get_level.short_description = "Уровень"

    list_display = (
        "name",
        "supplier",
        "get_level",
        "country",
        "city",
    )
    list_filter = ("city", "country")
    search_fields = ("name", "city", "country")

    @admin.action(description="Очистить задолженность")
    def clear_debt(self, request, queryset):
        queryset.update(debt=0.00)

    actions = [clear_debt]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "model", "release_date", "owner")
    list_filter = ("release_date", "owner__city", "owner__country")
    search_fields = ("title", "model", "owner__name")
    date_hierarchy = "release_date"
