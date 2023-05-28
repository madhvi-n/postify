from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db.models import Q
from graphene_django import DjangoObjectType
from graphql.error import GraphQLError
import graphene
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class Query(graphene.ObjectType):
    users = graphene.List(UserType)

    def resolve_users(self, info):
        return User.objects.all()


class CreateUserMutation(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    def mutate(self, info, username, password, email, first_name, last_name):
        try:
            user_exists = User.objects.filter(email=email).exists()
            if user_exists:
                raise GraphQLError('User with this email already exists')

            # Validate the password using Django's password validation
            validate_password(password)

            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            user.set_password(password)
            user.save()
            return CreateUserMutation(user=user)

        except ValidationError as e:
            raise GraphQLError(e.messages[0])

        except Exception as e:
            raise GraphQLError('Failed to create user')


class LoginUserMutation(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, email, password):
        try:
            validate_password(password)
            user = authenticate(email=email, password=password)
            if user is None:
                raise GraphQLError('Invalid email or password')

            if not user.is_active:
                raise GraphQLError('User account is disabled')

            login(info.context, user)
            return LoginUserMutation(user=user)
        except ValidationError as e:
            raise GraphQLError(e.messages[0])


class Mutation(graphene.ObjectType):
    create_user = CreateUserMutation.Field()
    login_user = LoginUserMutation.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
