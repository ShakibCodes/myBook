from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    display_name = models.CharField(max_length=100, blank=True)
    profile_photo = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    about = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.username