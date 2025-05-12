"""
Role model (the one I never had...).

License:
    MIT

"""

from mongoengine import *

from .user import User


class Role(Document):
    """
    Role model.

    This model represents a role in the system. It is used to manage
    user permissions and access levels.

    Attributes:
        name (str): The name of the role.

    """

    name: str = StringField(required=True, unique=True)
    users: list = ListField(ReferenceField(User, reverse_delete_rule=PULL), default=list)
