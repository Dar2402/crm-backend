from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("phone",)

    list_display = (
        "phone",
        "first_name",
        "last_name",
        "country_code",
        "city",
        "is_staff",
        "is_active",
    )

    search_fields = ("phone", "first_name", "last_name", "email", "city", "country_code")

    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Address / Location",
            {
                "fields": (
                    "country_code",
                    "state",
                    "city",
                    "address_line1",
                    "address_line2",
                    "postal_code",
                )
            },
        ),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone", "password1", "password2", "is_staff", "is_superuser"),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")
