"""
Permission model for actions.

License:
    MIT

"""

from mongoengine import PULL, Document, ListField, ReferenceField

from kamihi.bot.models import RegisteredAction

from .role import Role
from .user import User


class Permission(Document):
    """Permission model for actions."""

    action: RegisteredAction = ReferenceField(RegisteredAction, reverse_delete_rule=PULL)
    users: list[User] = ListField(ReferenceField(User, reverse_delete_rule=PULL), default=list)
    roles: list[Role] = ListField(ReferenceField(Role, reverse_delete_rule=PULL), default=list)
