from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    pass


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(max_length=300)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    image = models.ImageField(upload_to='images', blank=True)

    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"Posted on {self.date} by {self.owner.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="commentBy")
    text = models.TextField(max_length=300)

    def __str__(self):
        return f"Comment for {self.post} by {self.user.username}"


class Follower(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    follows = models.ManyToManyField(User, related_name="followers")

    def __str__(self):
        return f"Follower {self.follower}"


class Like(models.Model):
    postLiked = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    likedBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked")

    def __str__(self):
        return f"{self.postLiked} by {self.likedBy.username}"




