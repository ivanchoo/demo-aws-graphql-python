import json
import os
import random

_instance = None


class DataStore():

    @classmethod
    def instance(cls):
        global _instance
        if not _instance:
            _instance = cls()
        return _instance

    users = []
    friendships = {}

    def __init__(self, source=None):
        if not source:
            source = os.path.join(
                os.path.dirname(__file__),
                'users.json'
            )
        with open(source, 'r') as fp:
            self.users = json.load(fp)
        self._create_friendships()

    def get_user(self, user_id):
        return self.users[user_id - 1]

    def get_friends(self, user_id):
        if user_id not in self.friendships:
            return []
        friend_ids = self.friendships[user_id]
        return [self.get_user(friend_id) for friend_id in friend_ids]

    def _create_friendships(self):
        friendships = {}
        ids = list(range(1, len(self.users) + 1))
        for user_id in ids:
            num_friends = random.randint(3, 20)
            friend_ids = set(random.sample(ids, num_friends))
            if user_id in friend_ids:
                friend_ids.remove(user_id)
            friendships[user_id] = friend_ids
        self.friendships = friendships
