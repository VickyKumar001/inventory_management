from django.urls import path
# from .views import ItemCreateView, ItemRetrieveView, ItemUpdateView, ItemDeleteView
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, RegisterView, LoginView, ItemListView, ItemCRUDView


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)






urlpatterns = [
    path('', ItemListView.as_view(), name='item-list'),
    path('items/', ItemCRUDView.as_view(), name='item-list-create'), 
    path('items/<int:pk>/', ItemCRUDView.as_view(), name='item-detail'),  
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
]
