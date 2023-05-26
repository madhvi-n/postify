import graphene
from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Comment


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = ('id', 'author', 'author_id', 'post', 'comment',)

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


class CommentCreateUpdateInput(graphene.InputObjectType):
    comment = graphene.String(required=True)
    author = graphene.ObjectType()
    author_id = graphene.ID(required=True)


class Query(graphene.ObjectType):
    posts = graphene.List(
        CommentType,
        post_id=graphene.Int(required=True)
    )

    def resolve_posts(self, info, post_id):
        return Comment.objects.filter(post__id=post_id)


class CommentCreateMutation(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        input = CommentCreateUpdateInput(required=True)

    def mutate(root, info, input=None):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError('User is not authenticated')

        title = input.title
        comment_text = input.comment
        author_id = input.author_id

        author = None
        try:
            author = User.objects.get(id=author_id)
        except User.DoesNotExist:
            raise GraphQLError('Author not found.')

        comment = Comment.objects.create(
            comment=comment_text,
            author=author,
            content=content,
            published=True
        )
        return CommentCreateMutation(comment=comment)


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
    # update_comment = CommentUpdateMutation.Field()
    delete_comment = CommentDeleteMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
