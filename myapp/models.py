from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

# Create your models here.


class RssNews(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=2000)
    link = models.URLField(max_length=2000)
    pubdate = models.DateTimeField()
    description = models.TextField()
    image = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=100)
    read = models.BooleanField(default=False)
    favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class DefaultSetting(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    default_filter = models.CharField(max_length=100, default='all')

class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return self.user.username