from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=280)
    date = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts')

    def __str__(self):
        return f"Post {self.id} by {self.author.username}"
    

class Follow(models.Model):
    following = models.ForeignKey(User,on_delete=models.CASCADE, related_name="following")
    follower = models.ForeignKey(User,on_delete=models.CASCADE, related_name="follower")

    def __str__(self):
        return f"{self.following} is following {self.follower}"
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} likes {self.post}"