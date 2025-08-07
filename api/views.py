from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from .models import CustomUser, Product, WishlistItem, CartItem, Cart, Order, OrderItem
from .serializers import UserSerializer, ProductSerializer, WishlistItemSerializer, AddWishlistItemSerializer, CartSerializer, AddToCartSerializer, OrderSerializer
from .permissions import IsStoreManager
from django.db import transaction 

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStoreManager]

class PublicProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['=category']
    ordering_fields = ['popularity', 'price']

class WishlistListView(generics.ListAPIView):
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

class AddToWishlistView(generics.CreateAPIView):
    serializer_class = AddWishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

class RemoveFromWishlistView(generics.DestroyAPIView):
    queryset = WishlistItem.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user)

class CartView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        add_serializer = AddToCartSerializer(data=request.data)
        if add_serializer.is_valid():
            product_id = add_serializer.validated_data['product_id']
            quantity = add_serializer.validated_data['quantity']
            
            cart, _ = Cart.objects.get_or_create(user=request.user)
            product = Product.objects.get(id=product_id)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            if product.stock_count < cart_item.quantity:
                 return Response({"error": "Not enough stock available."}, status=status.HTTP_400_BAD_REQUEST)
            
            cart_serializer = CartSerializer(cart)
            return Response(cart_serializer.data, status=status.HTTP_200_OK)
        return Response(add_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "Product ID not provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except (Cart.DoesNotExist, CartItem.DoesNotExist):
            return Response({"error": "Item not in cart."}, status=status.HTTP_404_NOT_FOUND)
        
class CheckoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic 
    def post(self, request, *args, **kwargs):
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)

        cart_items = cart.items.all()
        if not cart_items:
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        grand_total = sum(item.quantity * item.product.price for item in cart_items)

        for item in cart_items:
            if item.product.stock_count < item.quantity:
                return Response(
                    {"error": f"Not enough stock for {item.product.name}. Available: {item.product.stock_count}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        order = Order.objects.create(user=request.user, total_paid=grand_total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price_at_purchase=item.product.price,
                quantity=item.quantity
            )
            item.product.stock_count -= item.quantity
            item.product.save()
        
        cart.items.all().delete()

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)