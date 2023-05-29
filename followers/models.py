from django.db import models
from django.contrib.auth.models import User
from posts.models import Tag


class UserFollower(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_followers"
    )
    followed_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User Follower"
        verbose_name_plural = "User Followers"

    def __str__(self):
        return f"{self.follower.username} is following {self.followed_user.username}"


class UserTag(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_tags"
    )
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User Tag"
        verbose_name_plural = "User Tags"

    def __str__(self):
        return f"{self.follower.username} is following {self.tag.name}"
