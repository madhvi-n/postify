from django.contrib import admin
from posts.models import Post, Tag, Category

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'title', 'author', 'published', 'is_archived', 'is_featured', 'comments_enabled')
    list_filter = ('published', 'category')
    list_editable = ('is_archived', 'is_featured', 'comments_enabled',)
    search_fields = ('title', 'content', 'author__username')
    raw_id_fields = ('author', 'category',)
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['tags']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
