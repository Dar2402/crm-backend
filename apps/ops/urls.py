from django.urls import path
from .views import (
    DashboardSummaryView,
    BookingsByStageView,
    BookingTrendView,
    OpsBookingsView,
    OpsCandidatesView,
    ExportBookingsCSV,
)

urlpatterns = [
    path("dashboard/summary/", DashboardSummaryView.as_view()),
    path("dashboard/bookings-by-stage/", BookingsByStageView.as_view()),
    path("dashboard/booking-trend/", BookingTrendView.as_view()),

    path("data/bookings/", OpsBookingsView.as_view()),
    path("data/candidates/", OpsCandidatesView.as_view()),

    path("export/bookings/", ExportBookingsCSV.as_view()),
]
