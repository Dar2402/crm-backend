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

    def save_model(self, request, obj, form, change):
        if change:
            old_obj = Booking.objects.get(pk=obj.pk)
            old_stage = old_obj.current_stage
            new_stage = obj.current_stage

            if old_stage != new_stage:

                StageHistory.objects.create(
                    booking=obj,
                    stage=new_stage,
                    remarks=f"Stage changed by admin {request.user.username}",
                )


                if new_stage.name.lower() == "medical":
                    obj.candidate.status = "booked"
                elif new_stage.name.lower() == "deployed":
                    obj.candidate.status = "deployed"
                elif new_stage.name.lower() == "rejected":
                    obj.status = "rejected"

                obj.candidate.save(update_fields=["status"])

        super().save_model(request, obj, form, change)


@admin.register(ApplicationStage)
class ApplicationStageAdmin(admin.ModelAdmin):
    list_display = ("order", "name")
    ordering = ("order",)
