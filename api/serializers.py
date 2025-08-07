from rest_framework import serializers
from .models import CustomUser, Product, WishlistItem, Cart, CartItem, Order, OrderItem

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

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'sub_total']
    
    def get_sub_total(self, obj):
        return obj.quantity * obj.product.price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'grand_total']

    def get_grand_total(self, obj):
        return sum(item.quantity * item.product.price for item in obj.items.all())


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            if product.stock_count < self.initial_data['quantity']:
                raise serializers.ValidationError("Not enough stock available.")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return value
    
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'price_at_purchase', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField() # Display the username

    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'total_paid', 'items']

class SalesDataSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    product_category = serializers.CharField(source='category')
    total_quantity_sold = serializers.IntegerField()

    class Meta:
        fields = ['product_id', 'product_name', 'product_category', 'total_quantity_sold']