from django.urls import path

from . import views

urlpatterns = [
    path('signup/', views.UserCreate.as_view(), name='signup'),
    path('token/', views.TokenAPIView.as_view(), name='token')
]
