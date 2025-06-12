from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Listing, Category, Review
from .serializers import (
    ListingListSerializer, ListingDetailSerializer, ListingCreateUpdateSerializer,
    CategorySerializer, ReviewSerializer
)
from .filters import ListingFilter


class CategoryListView(generics.ListCreateAPIView):
    """
    API endpoint for listing categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ListingListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing all travel listings and creating new ones
    """
    queryset = Listing.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price_per_night', 'rating', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingCreateUpdateSerializer
        return ListingListSerializer
    
    @swagger_auto_schema(
        operation_description="Get all travel listings with filtering and search capabilities",
        manual_parameters=[
            openapi.Parameter('location', openapi.IN_QUERY, description="Filter by location", type=openapi.TYPE_STRING),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price per night", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price per night", type=openapi.TYPE_NUMBER),
            openapi.Parameter('listing_type', openapi.IN_QUERY, description="Type of listing", type=openapi.TYPE_STRING),
            openapi.Parameter('search', openapi.IN_QUERY, description="Search in title, description, location", type=openapi.TYPE_STRING),
        ],
        responses={200: ListingListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new travel listing",
        request_body=ListingCreateUpdateSerializer,
        responses={201: ListingDetailSerializer}
    )
    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting individual listings
    """
    queryset = Listing.objects.filter(is_active=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ListingCreateUpdateSerializer
        return ListingDetailSerializer
    
    def get_permissions(self):
        """
        Only listing owners can update/delete their listings
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]
    
    def perform_update(self, serializer):
        # Only allow the host to update their own listing
        if self.get_object().host != self.request.user:
            raise PermissionError("You can only update your own listings")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow the host to delete their own listing
        if instance.host != self.request.user:
            raise PermissionError("You can only delete your own listings")
        # Soft delete - just mark as inactive
        instance.is_active = False
        instance.save()


class ListingReviewListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing reviews
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        listing_id = self.kwargs['listing_id']
        return Review.objects.filter(listing_id=listing_id)
    
    def perform_create(self, serializer):
        listing_id = self.kwargs['listing_id']
        listing = get_object_or_404(Listing, id=listing_id)
        serializer.save(reviewer=self.request.user, listing=listing)


@swagger_auto_schema(
    method='get',
    operation_description="Get API status and available endpoints",
    responses={
        200: openapi.Response(
            description="API status information",
            examples={
                "application/json": {
                    "message": "ALX Travel App API is running",
                    "version": "1.0",
                    "status": "active",
                    "endpoints": {
                        "listings": "/api/v1/listings/",
                        "categories": "/api/v1/categories/",
                        "documentation": "/swagger/"
                    }
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([])
def api_status(request):
    """
    Return API status and available endpoints
    """
    data = {
        "message": "ALX Travel App API is running",
        "version": "1.0",
        "status": "active",
        "endpoints": {
            "listings": "/api/v1/listings/",
            "categories": "/api/v1/categories/",
            "documentation": "/swagger/"
        },
        "total_listings": Listing.objects.filter(is_active=True).count(),
        "total_categories": Category.objects.count(),
    }
    return Response(data, status=status.HTTP_200_OK)
