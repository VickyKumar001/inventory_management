from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Item

class ItemTests(APITestCase):
    def test_create_item(self):
        url = reverse('item-list')
        data = {'name': 'TestItem' , 'description': 'TestDescription', 'quantity': 1, 'price': 10.99}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)