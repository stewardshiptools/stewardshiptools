from django.shortcuts import render

from rest_framework import viewsets, filters, permissions

from .models import LeafletMap
from .serializers import LeafletMapSerializer


# Rest framework viewsets
class LeafletMapViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = LeafletMap.objects.all()
    serializer_class = LeafletMapSerializer
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    #search_fields = ()
    ordering_fields = '__all__'
    ordering = ('name',)  # Default sort field.
