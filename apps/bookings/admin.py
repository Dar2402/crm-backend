from django.contrib import admin

from .models import Booking, ApplicationStage, StageHistory
from .services.workflow import BookingWorkflowService


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

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Booking.objects.get(pk=obj.pk)
            if old_obj.current_stage != obj.current_stage:
                BookingWorkflowService.move_stage(
                    booking=obj,
                    new_stage=obj.current_stage,
                    remarks=f"Stage changed by admin {request.user.username}",
                )
        else:
            super().save_model(request, obj, form, change)


@admin.register(ApplicationStage)
class ApplicationStageAdmin(admin.ModelAdmin):
    list_display = ("order", "name")
    ordering = ("order",)
