import posts.schema
import comments.schema
import profiles.schema
import likes.schema
import graphene
import graphql_jwt


class Query(
    posts.schema.Query,
    comments.schema.Query,
    profiles.schema.Query,
    likes.schema.Query,
    graphene.ObjectType,
):
    pass


class Mutation(
    posts.schema.Mutation,
    comments.schema.Mutation,
    profiles.schema.Mutation,
    likes.schema.Mutation,
    graphene.ObjectType,
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
