from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import OrderingFilter, SearchFilter
from .models import CustomUser, Product
from .serializers import UserSerializer, ProductSerializer
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