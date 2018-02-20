import graphene
from graphene import relay
from .datastore import DataStore


class User(graphene.ObjectType):

    class Meta:
        interfaces = [relay.Node]

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

    friends = relay.ConnectionField('demo.schema.UserConnection')

    def resolve_friends(self, info):
        friends = DataStore.instance().get_friends(self.user_id)
        return [User(**friend) for friend in friends]


class UserConnection(relay.Connection):

    class Meta:
        node = User


class Query(graphene.ObjectType):

    user = graphene.Field(User, user_id=graphene.Int())

    def resolve_user(self, info, user_id=1):
        data = DataStore.instance().get_user(user_id)
        return User(**data)


schema = graphene.Schema(
    query=Query
)
