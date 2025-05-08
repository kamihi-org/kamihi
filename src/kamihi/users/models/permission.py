"""
Permission model for actions.

License:
    MIT

"""

from mongoengine import *

from kamihi.bot.models.registered_action import RegisteredAction
from kamihi.users.models import Role, User


class Permission(Document):
    """Permission model for actions."""

    action: RegisteredAction = ReferenceField(RegisteredAction, reverse_delete_rule=PULL)
    users: list[User] = ListField(ReferenceField(User, reverse_delete_rule=PULL), default=list)
    roles: list[Role] = ListField(ReferenceField(Role, reverse_delete_rule=PULL), default=list)
