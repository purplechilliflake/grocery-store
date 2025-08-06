# api/views.py

from rest_framework import generics, viewsets
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