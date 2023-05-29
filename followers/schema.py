from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
from posts.schema import PostType
from followers.models import UserFollower, UserTag
from profiles.schema import UserType
import graphene


class UserFollowerType(DjangoObjectType):
    class Meta:
        model = UserFollower
        fields = ("id", "follower", "followed_user", "created_at")

    user_id = graphene.Int()
    user = graphene.Field(UserType)

    def resolve_user_id(self, info):
        return self.user_id

    def resolve_user(self, info):
        return self.user


class UserTagType(DjangoObjectType):
    class Meta:
        model = UserTag
        fields = ("id", "follower", "tag", "created_at")

    user_id = graphene.Int()
    user = graphene.Field(UserType)

    def resolve_user_id(self, info):
        return self.user_id

    def resolve_user(self, info):
        return self.user


class Query(graphene.ObjectType):
    user_tag_follower_count = graphene.Int(tag_id=graphene.Int(required=True))
    user_follower_count = graphene.Int(user_id=graphene.Int(required=True))
    posts_by_followed_tags = graphene.List(PostType)

    def resolve_user_tag_follower_count(self, info, tag_id):
        return UserTag.objects.filter(tag__id=tag_id).count()

    def resolve_user_followers_count(self, info, user_id):
        return UserFollower.objects.filter(followed_user__id=user_id).count()

    def resolve_posts_by_followed_tags(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        followed_tags = user.user_tags.values_list("tag", flat=True)
        posts = Post.objects.filter(tags__in=followed_tags)
        return posts


class FollowUserMutation(graphene.Mutation):
    user_follower = graphene.Field(UserFollowerType)

    class Arguments:
        follower_id = graphene.Int(required=True)
        followed_user_id = graphene.Int(required=True)

    def mutate(self, info, followed_user_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        try:
            followed_user = User.objects.get(id=followed_user_id)
            user_follower, created = UserFollower.objects.get_or_create(
                follower=user, followed_user=followed_user
            )
            return FollowUserMutation(follower=user_follower)
        except User.DoesNotExist:
            raise GraphQLError("User not found")


class UnfollowUserMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        user_follower_id = graphene.Int(required=True)

    def mutate(self, info, user_follower_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        try:
            user_follower = UserFollower.objects.get(id=user_follower_id, follower=user)
            user_follower.delete()
            return UnfollowUserMutation(success=True)
        except UserFollower.DoesNotExist:
            raise GraphQLError(
                "UserFollower not found or you are not authorized to unfollow"
            )


class CreateUserTagMutation(graphene.Mutation):
    user_tag = graphene.Field(UserTagType)

    class Arguments:
        tag_id = graphene.Int(required=True)

    def mutate(self, info, tag_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        try:
            tag = Tag.objects.get(id=tag_id)
            user_tag, created = UserTag.objects.get_or_create(tag=tag, follower=user)
            return CreateUserTagMutation(user_tag=user_tag)
        except Tag.DoesNotExist:
            raise GraphQLError("Tag not found")


class RemoveUserTagMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        user_tag_id = graphene.Int(required=True)

    def mutate(self, info, user_tag_id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("User is not authenticated")
        try:
            user_tag = UserTag.objects.get(id=user_tag_id)
            if user_tag.follower != user:
                raise GraphQLError("User is not authorized")

            user_tag.delete()
            return RemoveUserTagMutation(success=True)
        except UserTag.DoesNotExist:
            raise GraphQLError("User tag not found")


class Mutation(graphene.ObjectType):
    follow_user = FollowUserMutation.Field()
    unfollow_user = UnfollowUserMutation.Field()
    create_user_tag = CreateUserTagMutation.Field()
    remove_user_tag = RemoveUserTagMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
