from django.contrib import admin
from .models import (
    Candidate,
    CandidateExperience,
    CandidateSkill,
    CandidatePassport,
    CandidateMedical,
    CandidatePhoto,
)


class CandidatePhotoInline(admin.TabularInline):
    model = CandidatePhoto
    extra = 1


class CandidateExperienceInline(admin.TabularInline):
    model = CandidateExperience
    extra = 1


class CandidateSkillInline(admin.TabularInline):
    model = CandidateSkill
    extra = 1


class CandidatePassportInline(admin.StackedInline):
    model = CandidatePassport
    extra = 0


class CandidateMedicalInline(admin.StackedInline):
    model = CandidateMedical
    extra = 0


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("full_name", "nationality", "applied_for", "status", "price_sar")
    search_fields = ("full_name", "nationality", "applied_for")
    list_filter = ("status", "nationality")

    inlines = [
        CandidatePhotoInline,
        CandidateExperienceInline,
        CandidateSkillInline,
        CandidatePassportInline,
        CandidateMedicalInline,
    ]
