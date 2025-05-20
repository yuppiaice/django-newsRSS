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

# class User(AbstractUser):
#     # id = models.IntegerField(primary_key=True, default=createid, unique=True)
#     # name = models.CharField(max_length=100)
#     # email = models.EmailField(max_length=100, unique=True)
#     # password = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.username

