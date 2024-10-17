import logging
from rest_framework import status, generics
from .models import Item, CustomUser
from .serializers import ItemSerializer, CustomUserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from django.http import Http404



class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        logger.debug(f'User logged in: {request.user.username} with ID: {request.user.id}')
        return Response({
            'access': response.data['access'],
            'refresh': response.data['refresh'],
            'user_id': request.user.id,
            'username': request.user.username
        })

class CustomTokenRefreshView(TokenRefreshView):
    pass

logger = logging.getLogger('user_activity')

# Registration View Class
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the user and save it
        user = serializer.save()

        # Hash the password and save
        password = request.data.get('password')
        user.set_password(password)
        user.save()

        logger.debug(f'User created: {user.username} with ID: {user.id}')

        # Automatically log in the user after registration
        user = authenticate(username=user.username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
            }, status=status.HTTP_201_CREATED)

        logger.warning(f'User created but failed to log in: {user.username}')
        return Response({
            'error': 'User created but failed to log in'
        }, status=status.HTTP_401_UNAUTHORIZED)

# Login View Class
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        logger.debug(f'Attempting login for username: {username}')

        cache_key = f"login_attempts_{username}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= 5:
            logger.warning(f"User {username} is rate-limited due to too many login attempts.")
            return Response({"error": "Too many login attempts. Try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            logger.debug(f'User logged in: {username} with ID: {user.id}')
            cache.delete(cache_key)  

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'username': user.username,
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f'Failed login attempt for username: {username}')
            cache.set(cache_key, attempts + 1, timeout=60 * 60)  
            return Response({
                'error': 'Invalid username or password'
            }, status=status.HTTP_401_UNAUTHORIZED)





class ItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, *args, **kwargs):
        
        if pk:
            cache_key = f'item_{pk}'  
            item_data = cache.get(cache_key)

            if item_data is None:
                logger.debug(f"Cache miss for item ID {pk}: Fetching from database.")
                item = get_object_or_404(Item, pk=pk)
                item_data = ItemSerializer(item).data
                cache.set(cache_key, item_data, timeout=300) 
            else:
                logger.debug(f"Cache hit for item ID {pk}: Serving from Redis cache.")
            return Response(item_data, status=status.HTTP_200_OK)

        
        cache_key = 'item_list'  
        items_data = cache.get(cache_key)

        if items_data is None:
            logger.debug("Cache miss: Fetching all items from database.")
            items = Item.objects.all()
            if not items:
                return Response({"detail": "No items available"}, status=status.HTTP_404_NOT_FOUND)
            items_data = ItemSerializer(items, many=True).data
            cache.set(cache_key, items_data, timeout=3600)  
        else:
            logger.debug("Cache hit: Serving all items from Redis cache.")

        return Response(items_data, status=status.HTTP_200_OK)



class ItemCRUDView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a new item"""
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            logger.debug(f'Item created: {item.name} with ID: {item.id} by user ID: {request.user.id}')
            cache.delete('item_list')  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f'Item creation failed due to invalid data: {serializer.errors}')
            return Response({
                "error": "Item already exists",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, pk=None):
        """Retrieve a specific item by ID or return all items if no ID is provided."""
        if pk:
            cache_key = f'item_{pk}'  
            item_data = cache.get(cache_key)

            if item_data is None:
                logger.debug(f"Cache miss for item ID {pk}: Fetching from database.")
                item = get_object_or_404(Item, pk=pk)
                item_data = ItemSerializer(item).data
                cache.set(cache_key, item_data, timeout=300)  
            else:
                logger.debug(f"Cache hit for item ID {pk}: Serving from Redis cache.")
            return Response(item_data, status=status.HTTP_200_OK)

    
        cache_key = 'item_list'  
        items_data = cache.get(cache_key)

        if items_data is None:
            logger.debug("Cache miss: Fetching all items from database.")
            items = Item.objects.all()
            if not items:
                return Response({"detail": "No items available"}, status=status.HTTP_404_NOT_FOUND)
            items_data = ItemSerializer(items, many=True).data
            cache.set(cache_key, items_data, timeout=3600)  
        else:
            logger.debug("Cache hit: Serving all items from Redis cache.")

        return Response(items_data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        serializer = ItemSerializer(item, data=request.data, partial=True)
    
        if serializer.is_valid():
            updated_item = serializer.save()
            logger.debug(f'Item updated: {updated_item.name} with ID: {updated_item.id} by user ID: {request.user.id}')
            cache.delete('item_list')  
            return Response(serializer.data, status=status.HTTP_200_OK)
    
        logger.error(f'Item update failed due to invalid data: {serializer.errors}')
        return Response({
            "error": "Invalid data provided",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete an item"""
        item = get_object_or_404(Item, pk=pk)
        logger.debug(f'Attempting to delete item with ID: {pk}')
        item.delete()
        cache.delete('item_list')  
        logger.debug(f'Item deleted: {item.name} with ID: {item.id} by user ID: {request.user.id}')
        return Response(status=status.HTTP_204_NO_CONTENT)






