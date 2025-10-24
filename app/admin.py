from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "full_name",
        "phone",
        "formatted_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("lastname", "firstname", "phone", "reference")
    readonly_fields = ("reference", "created_at", "updated_at")
    list_per_page = 20

    fieldsets = (
        ("Informations personnelles", {"fields": ("lastname", "firstname", "phone")}),
        ("Détails du paiement", {"fields": ("amount", "status", "reference")}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by("-created_at")
