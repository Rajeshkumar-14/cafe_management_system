from django.contrib import admin
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear
from .models import Tables, Dishes, OrderList, TempOrderList

__project_by__ = "RajeshKumar"

class OrderListAdmin(admin.ModelAdmin):
    list_display = ("table", "total_amount", "formatted_created_at", "attended_by_name")
    search_fields = ("table__name", "attended_by__username")
    list_filter = ("table", "created_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("table", "attended_by")

    def attended_by_name(self, obj):
        return obj.attended_by.username

    def get_total_amount(self, queryset):
        return queryset.aggregate(total_amount=Sum("total_amount"))["total_amount"] or 0

    def get_total_amount_for_period(self, period):
        queryset = OrderList.objects.filter(created_at__date=timezone.now().date())
        if period == "month":
            queryset = (
                queryset.annotate(month=TruncMonth("created_at"))
                .values("month")
                .annotate(total_amount=Sum("total_amount"))
            )
        elif period == "year":
            queryset = (
                queryset.annotate(year=TruncYear("created_at"))
                .values("year")
                .annotate(total_amount=Sum("total_amount"))
            )
        return self.get_total_amount(queryset)

    def changelist_view(self, request, extra_context=None):
        today_total = self.get_total_amount(
            OrderList.objects.filter(created_at__date=timezone.now().date())
        )
        month_total = self.get_total_amount_for_period("month")
        year_total = self.get_total_amount_for_period("year")
        previous_year_total = self.get_total_amount_for_period("previous_year")

        extra_context = extra_context or {}
        extra_context["today_total"] = today_total
        extra_context["month_total"] = month_total
        extra_context["year_total"] = year_total
        extra_context["previous_year_total"] = previous_year_total

        return super().changelist_view(request, extra_context=extra_context)

    def formatted_created_at(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    formatted_created_at.short_description = "Created At"


class TablesAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")
    search_fields = ("name", "created_by__username")
    list_filter = ("created_at",)


class DishesAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "created_by", "created_at")
    search_fields = ("name", "created_by__username")
    list_filter = ("created_at",)


admin.site.register(Tables, TablesAdmin)
admin.site.register(Dishes, DishesAdmin)
admin.site.register(OrderList, OrderListAdmin)
admin.site.register(TempOrderList)
