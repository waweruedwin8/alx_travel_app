
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Category, ListingImage, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'caption', 'is_primary', 'order', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewer_name', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['reviewer']


class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'date_joined']


class ListingListSerializer(serializers.ModelSerializer):
    """Serializer for listing list view (less detailed)"""
    host_name = serializers.CharField(source='host.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'location', 'price_per_night', 'listing_type',
            'category_name', 'max_guests', 'bedrooms', 'bathrooms', 'rating',
            'total_reviews', 'host_name', 'primary_image', 'featured', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
        return None


class ListingDetailSerializer(serializers.ModelSerializer):
    """Serializer for listing detail view (more detailed)"""
    host = HostSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    amenities_list = serializers.ReadOnlyField()
    
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'location', 'address', 'price_per_night',
            'listing_type', 'category', 'max_guests', 'bedrooms', 'bathrooms',
            'rating', 'total_reviews', 'latitude', 'longitude', 'amenities',
            'amenities_list', 'house_rules', 'check_in_time', 'check_out_time',
            'minimum_nights', 'maximum_nights', 'host', 'images', 'reviews',
            'featured', 'created_at', 'updated_at'
        ]


class ListingCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating listings"""
    
    class Meta:
        model = Listing
        fields = [
            'title', 'description', 'location', 'address', 'price_per_night',
            'listing_type', 'category', 'max_guests', 'bedrooms', 'bathrooms',
            'latitude', 'longitude', 'amenities', 'house_rules', 'check_in_time',
            'check_out_time', 'minimum_nights', 'maximum_nights'
        ]
    
    def validate_price_per_night(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per night must be greater than 0")
        return value
    
    def validate_maximum_nights(self, value):
        minimum_nights = self.initial_data.get('minimum_nights', 1)
        if value < minimum_nights:
            raise serializers.ValidationError("Maximum nights must be greater than or equal to minimum nights")
        return value
