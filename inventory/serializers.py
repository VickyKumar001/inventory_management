from rest_framework import serializers
from .models import Item, CustomUser

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'quantity', 'price', 'created_at', 'updated_at']

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password']
        
