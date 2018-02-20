import graphene
from .datastore import DataStore


class User(graphene.ObjectType):

    user_id = graphene.Int()
    email = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    avatar_url = graphene.String()
    gender = graphene.String()
    job = graphene.String()
    education = graphene.String()
    address = graphene.String()
    introduction = graphene.String()

    def resolve_email(self, info):
        return '123'


class Query(graphene.ObjectType):

    user = graphene.Field(User, user_id=graphene.Int())

    def resolve_user(self, info, user_id=1):
        user = User(**DataStore.instance().get_user(user_id))
        return user


schema = graphene.Schema(
    query=Query
)
