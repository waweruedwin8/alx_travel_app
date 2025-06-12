from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    # API status
    path('', views.api_status, name='api-status'),
    
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    
    # Listings
    path('listings/', views.ListingListCreateView.as_view(), name='listing-list'),
    path('listings/<uuid:pk>/', views.ListingDetailView.as_view(), name='listing-detail'),
    
    # Reviews
    path('listings/<uuid:listing_id>/reviews/', views.ListingReviewListCreateView.as_view(), name='listing-reviews'),
]
