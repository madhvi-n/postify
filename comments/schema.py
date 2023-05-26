import graphene
from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Comment
from posts.models import Post


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ('id', 'author', 'author_id', 'post', 'comment',)

    author_id = graphene.Int()
    author = graphene.Field(UserType)


    def resolve_author_id(self, info):
        return self.author_id

    def resolve_author(self, info):
        if self.author_id:
            return User.objects.get(id=self.author_id)
        return None


class CommentCreateInput(graphene.InputObjectType):
    comment = graphene.String(required=True)
    author = graphene.ObjectType()
    author_id = graphene.ID(required=True)
    post_id = graphene.ID(required=True)

class CommentUpdateInput(graphene.InputObjectType):
    comment = graphene.String(required=True)
    comment_id = graphene.ID(required=True)


class Query(graphene.ObjectType):
    comments = graphene.List(
        CommentType,
        post_id=graphene.Int(required=True)
    )

    def resolve_posts(self, info, post_id):
        return Comment.objects.filter(post__id=post_id)


class CommentCreateMutation(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        input = CommentCreateInput(required=True)

    def mutate(self, info, input=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('User is not authenticated')

        comment_text = input.comment
        author_id = input.author_id
        post_id = input.post_id
        try:
            author = User.objects.get(id=author_id)
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.create(
                comment=comment_text,
                author=author,
                post=post
            )
            return CommentCreateMutation(comment=comment)
        except User.DoesNotExist:
            raise GraphQLError('Author not found.')
        except Post.DoesNotExist:
            raise GraphQLError('Post not found')


class CommentUpdateMutation(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        input = CommentUpdateInput(required=True)

    def mutate(self, info, input=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('User is not authenticated')

        comment_text = input.comment
        comment_id = input.comment_id
        try:
            comment = Comment.objects.get(id=comment_id)
            if comment.author != user:
                raise GraphQLError('User is not the author of the comment')
                
            comment.comment = comment_text
            comment.save()
            return CommentUpdateMutation(comment=comment)
        except Comment.DoesNotExist:
            raise GraphQLError('Comment not found.')


class CommentDeleteMutation(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('User is not authenticated')

        comment = Comment.objects.get(id=id)
        if comment is None:
            raise GraphQLError('Comment not found.')

        if comment.author != user:
            raise GraphQLError('Bad Request. User is not the author of this comment')

        comment.delete()
        return CommentDeleteMutation(success=True)


class Mutation(graphene.ObjectType):
    create_comment = CommentCreateMutation.Field()
    update_comment = CommentUpdateMutation.Field()
    delete_comment = CommentDeleteMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
