from rest_framework import status, generics
from .models import Item
from .serializers import ItemSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import CustomUserSerializer

class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return Response({
            'access': response.data['access'],
            'refresh': response.data['refresh'],
            'user_id': request.user.id,
            'username': request.user.username
        })

class CustomTokenRefreshView(TokenRefreshView):
    pass

# POST: Create Item
class ItemCreateView(generics.CreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

# GET: Retrieve Item
class ItemRetrieveView(generics.RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        item_id = self.kwargs['pk']
        # Check if item is cached
        cached_item = cache.get(f'item_{item_id}')
        if cached_item:
            return cached_item
        # If not, fetch from DB and cache it
        item = super().get_object()
        cache.set(f'item_{item_id}', item, timeout=3600)  # Cache for 1 hour
        return item

# PUT: Update Item
class ItemUpdateView(generics.UpdateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

# DELETE: Delete Item
class ItemDeleteView(generics.DestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
