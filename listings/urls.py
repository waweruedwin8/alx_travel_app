from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('listings/', views.ListingListView.as_view(), name='listing-list'),
]