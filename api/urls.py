from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, 
    ProductViewSet, 
    PublicProductListView,
    WishlistListView,
    AddToWishlistView,
    RemoveFromWishlistView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('browse-products/', PublicProductListView.as_view(), name='public-products'),
    path('wishlist/', WishlistListView.as_view(), name='wishlist-list'),
    path('wishlist/add/', AddToWishlistView.as_view(), name='wishlist-add'),
    path('wishlist/remove/<int:pk>/', RemoveFromWishlistView.as_view(), name='wishlist-remove'),
    path('', include(router.urls)),
]