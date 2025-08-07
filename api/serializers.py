from rest_framework import serializers
from .models import CustomUser, Product, WishlistItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username = validated_data['username'],
            email = validated_data.get('email', ''),
            password = validated_data['password'],
            role = validated_data.get('role', 'customer')
        )

        return user
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'added_at']


class AddWishlistItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = WishlistItem
        fields = ['product_id']

    def create(self, validated_data):
        user = self.context['request'].user
        product_id = validated_data['product_id']
        
        wishlist_item, created = WishlistItem.objects.get_or_create(user=user, product_id=product_id)
        return wishlist_item