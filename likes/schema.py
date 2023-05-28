import graphene
from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
from django.contrib.auth.models import User
from django.db.models import Q
from .models import PostLike, CommentLike
from posts.models import Post
from profiles.schema import UserType
from comments.models import Comment


class PostLikeType(DjangoObjectType):
    class Meta:
        model = PostLike
        fields = ("id", "post", "user", "created_at")

    user_id = graphene.Int()
    user = graphene.Field(UserType)

    def resolve_user_id(self, info):
        return self.user_id

    def resolve_user(self, info):
        return self.user


class CommentLikeType(DjangoObjectType):
    class Meta:
        model = CommentLike
        fields = ("id", "comment", "user", "created_at")

    user_id = graphene.Int()
    user = graphene.Field(UserType)

    def resolve_user_id(self, info):
        return self.user_id

    def resolve_user(self, info):
        return self.user


class Query(graphene.ObjectType):
    post_likes_count = graphene.Int(post_id=graphene.Int(required=True))
    comment_likes_count = graphene.Int(comment_id=graphene.Int(required=True))

    def resolve_post_likes_count(self, info, post_id):
        post = Post.objects.get(id=post_id)
        return post.likes.count()

    def resolve_comment_likes_count(self, info, comment_id):
        comment = Comment.objects.get(id=comment_id)
        return comment.likes.count()


class PostLikeCreateMutation(graphene.Mutation):
    like = graphene.Field(PostLikeType)

    class Arguments:
        post_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)

    def mutate(self, info, post_id, user_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        try:
            post = Post.objects.get(id=post_id)
            user = User.objects.get(id=user_id)
            post_like, created = PostLike.objects.get_or_create(post=post, user=user)
            return PostLikeCreateMutation(like=post_like)
        except User.DoesNotExist:
            raise GraphQLError("User not found")
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")


class PostLikeRemoveMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        like_id = graphene.Int(required=True)

    def mutate(self, info, like_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")

        try:
            post_like = PostLike.objects.get(id=like_id)
            if user != post_like.user:
                raise GraphQLError("Bad Request. User has not liked this post")
            post_like.delete()
            return PostLikeRemoveMutation(success=True)
        except User.DoesNotExist:
            raise GraphQLError("User not found")
        except Post.DoesNotExist:
            raise GraphQLError("Post not found")


class CommentLikeCreateMutation(graphene.Mutation):
    like = graphene.Field(CommentLikeType)

    class Arguments:
        comment_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)

    def mutate(self, info, comment_id, user_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")

        try:
            comment = Comment.objects.get(id=comment_id)
            user = User.objects.get(id=user_id)
            comment_like, created = CommentLike.objects.get_or_create(
                comment=comment, user=user
            )
            return CommentLikeCreateMutation(like=comment_like)
        except User.DoesNotExist:
            raise GraphQLError("User not found")
        except Comment.DoesNotExist:
            raise GraphQLError("Comment not found")


class CommentLikeRemoveMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        like_id = graphene.Int(required=True)

    def mutate(self, info, like_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")

        try:
            comment_like = CommentLike.objects.get(id=like_id)
            if user != comment_like.user:
                raise GraphQLError("Bad Request. User has not liked this post")
            comment_like.delete()
            return CommentLikeRemoveMutation(success=True)
        except User.DoesNotExist:
            raise GraphQLError("User not found")
        except Comment.DoesNotExist:
            raise GraphQLError("Comment not found")


class Mutation(graphene.ObjectType):
    like_post = PostLikeCreateMutation.Field()
    unlike_post = PostLikeRemoveMutation.Field()
    like_comment = CommentLikeCreateMutation.Field()
    unlike_comment = CommentLikeRemoveMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
