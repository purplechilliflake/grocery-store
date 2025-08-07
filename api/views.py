from rest_framework import generics, viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from .models import CustomUser, Product, WishlistItem
from .serializers import UserSerializer, ProductSerializer, WishlistItemSerializer, AddWishlistItemSerializer
from .permissions import IsStoreManager

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
