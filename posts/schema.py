import graphene
from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
from .models import Post, Tag, Category
from django.contrib.auth.models import User
from django.db.models import Q

class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ('id', 'name')


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = (
            'id', 'title', 'content', 'author', 'author_id', 'published',
            'comments_enabled', 'is_archived', 'is_featured', 'created_at',
            'updated_at', 'slug',
        )

    content = graphene.String()
    author_id = graphene.Int()
    author = graphene.Field(UserType)

    def resolve_content(self, info):
        return self.content

    def resolve_author_id(self, info):
        return self.author_id

    def resolve_author(self, info):
        if self.author_id:
            return User.objects.get(id=self.author_id)
        return None


class PostCreateUpdateInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    author = graphene.ObjectType()
    author_id = graphene.ID()
    author_username = graphene.String()


class Query(graphene.ObjectType):
    posts = graphene.List(
        PostType,
        published=graphene.Boolean(),
        author_username=graphene.String(),
        search=graphene.String()
    )

    def resolve_posts(self, info, published=None, author_username=None, search=None):
        queryset = Post.objects.all()

        if published is not None:
            queryset = queryset.filter(published=published)

        if author_username:
            queryset = queryset.filter(author__username=author_username)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        return queryset


class PostCreateMutation(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        input = PostCreateUpdateInput(required=True)

    def mutate(root, info, input=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('User is not authorized')

        title = input.title
        content = input.content
        author_id = input.author_id
        author_username = input.author_username

        # Resolve the author using either the provided ID or username
        author = None
        if author_id:
            try:
                author = User.objects.get(id=author_id)
            except User.DoesNotExist:
                raise GraphQLError('Author not found.')
        elif author_username:
            try:
                author = User.objects.get(username=author_username)
            except User.DoesNotExist:
                raise GraphQLError('Author not found.')

        post = Post.objects.create(
            title=title,
            author=author,
            content=content,
            published=True
        )
        return PostCreateMutation(post=post)


class PostUpdateMutation(graphene.Mutation):
    post = graphene.Field(PostType)

    class Arguments:
        id = graphene.ID(required=True)
        input = PostCreateUpdateInput(required=True)

    def mutate(self, info, id, input=None):

        try:
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError('User is not authorized')

            post = Post.objects.get(id=id)
            post.title = input.get('title', post.title)
            post.content = input.get('content', post.content)
            post.tags.set(input.get('tag_ids', list(post.tags.all())))
            post.category_id = input.get('category_id', post.category_id)
            post.save()
            return PostUpdateMutation(post=post)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found.')


class PostDeleteMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):

        try:
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError('User is not authorized')
            post = Post.objects.get(id=id)
            post.delete()
            return PostDeleteMutation(success=True)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found.')


class PostToggleArchiveMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        try:
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError('User is not authenticated')
            post = Post.objects.get(id=id)
            post.is_archived = not post.is_archived
            post.save()
            return PostToggleArchiveMutation(success=True)
        except Post.DoesNotExist:
            return GraphQLError('Post not found.')


class PostToggleFeatureMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        try:
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError('User is not authenticated')
            post = Post.objects.get(id=id)
            post.is_featured = not post.is_featured
            post.save()
            return PostToggleFeatureMutation(success=True)
        except Post.DoesNotExist:
            return GraphQLError('Post not found.')


class PostTogglePublishMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        try:
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError('User is not authenticated')
            post = Post.objects.get(id=id)
            post.published = not post.published
            post.save()
            return PostTogglePublishMutation(success=True)
        except Post.DoesNotExist:
            return GraphQLError('Post not found.')


class AddPostTagMutation(graphene.Mutation):
    tag = graphene.Field(TagType)

    class Arguments:
        id  = graphene.ID(required=True)
        tag_id = graphene.ID(required=True)

    def mutate(self, info, id, tag_id):
        try:
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError('User is not authenticated')
            post = Post.objects.get(id=id)
            tag = Tag.objects.get(id=tag_id)
            post.tags.add(tag)
            return AddPostTagMutation(tag=tag)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found')
        except Tag.DoesNotExist:
            raise GraphQLError('Tag not found')

class DeletePostTagMutation(graphene.Mutation):
    tag = graphene.Field(TagType)

    class Arguments:
        id  = graphene.ID(required=True)
        tag_id = graphene.ID(required=True)

    def mutate(self, info, id, tag_id):
        try:
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError('User is not authenticated')
            post = Post.objects.get(id=id)
            tag = Tag.objects.get(id=tag_id)
            if tag_id in post.tags.values_list('id'):
                raise GraphQLError('Tag does not exist in post')
            post.tags.remove(tag)
            return DeletePostTagMutation(success=True)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found')
        except Tag.DoesNotExist:
            raise GraphQLError('Tag not found')


class AddPostCategoryMutation(graphene.Mutation):
    category = graphene.Field(CategoryType)

    class Arguments:
        id  = graphene.ID(required=True)
        category_id = graphene.ID(required=True)

    def mutate(self, info, id, category_id):
        try:
            user = info.context.user
            if not user.is_authenticated:
                raise GraphQLError('User is not authenticated')
            post = Post.objects.get(id=id)
            category = Category.objects.get(id=category_id)
            post.category = category
            post.save()
            return AddPostCategoryMutation(category=category)
        except Post.DoesNotExist:
            raise GraphQLError('Post not found')
        except Category.DoesNotExist:
            raise GraphQLError('Category not found')

class Mutation(graphene.ObjectType):
    create_post = PostCreateMutation.Field()
    update_post = PostUpdateMutation.Field()
    delete_post = PostDeleteMutation.Field()
    post_toggle_archive = PostToggleArchiveMutation.Field()
    post_toggle_feature = PostToggleFeatureMutation.Field()
    post_toggle_publish = PostTogglePublishMutation.Field()
    add_post_tag = AddPostTagMutation.Field()
    delete_post_tag = DeletePostTagMutation.Field()
    add_post_category = AddPostCategoryMutation.Field()
    update_post_category = AddPostCategoryMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
