from django.urls import path
from .views import CandidateListView, CandidateDetailView

urlpatterns = [
    path("", CandidateListView.as_view()),
    path("<int:pk>/", CandidateDetailView.as_view()),
]
