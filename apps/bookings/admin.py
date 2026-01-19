from django.contrib import admin
from .models import Booking, ApplicationStage, StageHistory


class StageHistoryInline(admin.TabularInline):
    model = StageHistory
    extra = 0
    readonly_fields = ("updated_at",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "candidate", "current_stage", "status", "created_at")
    list_filter = ("status", "current_stage")
    search_fields = ("user__phone", "candidate__full_name")

    inlines = [StageHistoryInline]


@admin.register(ApplicationStage)
class ApplicationStageAdmin(admin.ModelAdmin):
    list_display = ("order", "name")
    ordering = ("order",)
