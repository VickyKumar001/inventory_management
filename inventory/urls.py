from django.urls import path
from .views import ItemCreateView, ItemRetrieveView, ItemUpdateView, ItemDeleteView
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, CreateUserView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)




urlpatterns = [
    path('items/', ItemCreateView.as_view(), name='item-create'),
    path('items/<int:pk>/', ItemRetrieveView.as_view(), name='item-detail'),
    path('items/<int:pk>/update/', ItemUpdateView.as_view(), name='item-update'),
    path('items/<int:pk>/delete/', ItemDeleteView.as_view(), name='item-delete'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', CreateUserView.as_view(), name='create-user'),
]
