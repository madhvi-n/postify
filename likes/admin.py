from django.contrib import admin
from likes.models import PostLike, CommentLike


# Register your models here.
@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    pass


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    pass
