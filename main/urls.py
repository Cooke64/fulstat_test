from rest_framework import routers
from django.urls import path, include

from main.views import ProductView, ProductStateView, TrackingView
from users.views import UserAPIView


router = routers.DefaultRouter()

router.register(r'products', ProductView, basename='products')
router.register(r'products_state', ProductStateView, basename='products_state')
router.register(r'products_tracking', TrackingView, basename='products_tracking')
router.register(r'users', UserAPIView, basename='users')

urlpatterns = [
    path('v1/auth/', include('users.urls')),
    path('v1/', include(router.urls)),
]