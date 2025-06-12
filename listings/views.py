from rest_framework import generics, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ListingListView(generics.ListAPIView):
    """
    API endpoint for retrieving travel listings.
    """
    
    @swagger_auto_schema(
        operation_description="Get all travel listings",
        responses={
            200: openapi.Response(
                description="List of travel listings",
                examples={
                    "application/json": {
                        "message": "Welcome to ALX Travel App API",
                        "version": "1.0",
                        "endpoints": {
                            "listings": "/api/v1/listings/",
                            "documentation": "/swagger/"
                        }
                    }
                }
            )
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Return a welcome message and API information.
        """
        data = {
            "message": "Welcome to ALX Travel App API",
            "version": "1.0",
            "endpoints": {
                "listings": "/api/v1/listings/",
                "documentation": "/swagger/"
            }
        }
        return Response(data, status=status.HTTP_200_OK)