from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Candidate
from .serializers import CandidateListSerializer, CandidateDetailSerializer


class CandidateListView(generics.ListAPIView):
    queryset = Candidate.objects.filter(status="available").prefetch_related(
        "photos", "experiences", "skills"
    )

    serializer_class = CandidateListSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["nationality", "applied_for", "status"]
    search_fields = ["full_name", "applied_for", "nationality"]


class CandidateDetailView(generics.RetrieveAPIView):
    queryset = Candidate.objects.all().prefetch_related(
        "photos", "experiences", "skills"
    ).select_related("passport", "medical")

    serializer_class = CandidateDetailSerializer
