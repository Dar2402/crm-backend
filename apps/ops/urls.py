from django.urls import path

from .views import (
    DashboardSummaryView,
    BookingsByStageView,
    BookingTrendView,
    OpsBookingsView,
    OpsCandidatesView,
    ExportBookingsCSV,
)
from .views_analytics import (
    FunnelAnalyticsView,
    AvgStageTimeView,
    TimeToDeployView,
)
from .views_auth import OpsLoginView
from .views_workflow import (
    MoveBookingStageView,
    RejectBookingView,
    DeployBookingView,
    OpsApplicationStageListView
)

urlpatterns = [
    path("auth/login/", OpsLoginView.as_view()),
    path("dashboard/summary/", DashboardSummaryView.as_view()),
    path("dashboard/bookings-by-stage/", BookingsByStageView.as_view()),
    path("dashboard/booking-trend/", BookingTrendView.as_view()),

    path("data/bookings/", OpsBookingsView.as_view()),
    path("data/candidates/", OpsCandidatesView.as_view()),

    path("export/bookings/", ExportBookingsCSV.as_view()),

    path("bookings/<int:pk>/move-stage/", MoveBookingStageView.as_view()),
    path("bookings/<int:pk>/reject/", RejectBookingView.as_view()),
    path("bookings/<int:pk>/deploy/", DeployBookingView.as_view()),
    path("analytics/funnel/", FunnelAnalyticsView.as_view()),
    path("analytics/avg-stage-time/", AvgStageTimeView.as_view()),
    path("analytics/time-to-deploy/", TimeToDeployView.as_view()),
    path("stages/", OpsApplicationStageListView.as_view()),
]
