from django.urls import path
from .views import CreateBookingView, MyBookingsView, BookingTimelineView

urlpatterns = [
    path("", CreateBookingView.as_view()),
    path("my/", MyBookingsView.as_view()),
    path("<int:pk>/timeline/", BookingTimelineView.as_view()),
]
