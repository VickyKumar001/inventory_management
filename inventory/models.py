from django.db import models
from django.contrib.auth.models import AbstractUser

class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=0)  
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    



class CustomUser(AbstractUser):
    username=models.CharField(max_length=100,unique=True)
    password=models.CharField(max_length=100)
    pass


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',  
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    