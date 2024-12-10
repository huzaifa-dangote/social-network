from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="followers")

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=False)
    likes = models.ManyToManyField(User, blank=True, related_name="liked_posts")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def likes_count(self):
        return self.likes.count()

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "likes": self.likes_count(),
            "liked_by": None
        }
