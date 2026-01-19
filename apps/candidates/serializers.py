from rest_framework import serializers
from .models import (
    Candidate,
    CandidatePhoto,
    CandidateExperience,
    CandidateSkill,
    CandidatePassport,
    CandidateMedical,
)


class CandidatePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatePhoto
        fields = ["id", "image"]


class CandidateExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateExperience
        fields = ["job_title", "country", "city", "period_years"]


class CandidateSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSkill
        fields = ["skill_name"]


class CandidatePassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidatePassport
        fields = [
            "passport_type",
            "date_of_issue",
            "date_of_expiry",
            "place_of_issue",
            "passport_in_office",
        ]


class CandidateMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateMedical
        fields = ["is_medically_fit", "remarks"]


class CandidateListSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            "id",
            "full_name",
            "age",
            "nationality",
            "applied_for",
            "expected_salary",
            "price_sar",
            "status",
            "photo",
        ]

    def get_photo(self, obj):
        photo = obj.photos.first()
        if photo:
            return photo.image.url
        return None


class CandidateDetailSerializer(serializers.ModelSerializer):
    photos = CandidatePhotoSerializer(many=True)
    experiences = CandidateExperienceSerializer(many=True)
    skills = CandidateSkillSerializer(many=True)
    passport = CandidatePassportSerializer()
    medical = CandidateMedicalSerializer()

    class Meta:
        model = Candidate
        fields = "__all__"
