"""
Internal models for Kamihi.

License:
    MIT

"""

from sqlmodel import Field, SQLModel, Relationship


class RegisteredAction(SQLModel, table=True):
    """
    RegisteredAction model.

    This model represents an action that is registered in the system.
    It is used to manage user actions and their associated data.

    Attributes:
        name (str): The name of the action.
        description (str): A description of the action.

    """

    id : int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)
    description: str | None = None
    permissions: list["Permission"] = Relationship(back_populates="action", cascade_delete=True)


class UserRoleLink(SQLModel, table=True):
    """
    Association table for many-to-many relationship between User and Role.

    Attributes:
        user_id (int): The ID of the user.
        role_id (int): The ID of the role.
    """

    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)


class PermissionUserLink(SQLModel, table=True):
    """
    Association table for many-to-many relationship between Permission and User.

    Attributes:
        permission_id (int): The ID of the permission.
        user_id (int): The ID of the user.
    """

    permission_id: int | None = Field(default=None, foreign_key="permission.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)


class PermissionRoleLink(SQLModel, table=True):
    """
    Association table for many-to-many relationship between Permission and Role.

    Attributes:
        permission_id (int): The ID of the permission.
        role_id (int): The ID of the role.
    """

    permission_id: int | None = Field(default=None, foreign_key="permission.id", primary_key=True)
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)


class User(SQLModel, table=True):
    """
    User model.

    This model represents a user in the system.
    It is used to manage user information and their associated data.

    Attributes:
        telegram_id (int): The Telegram ID of the user.
        is_admin (bool): Whether the user has admin privileges.

    """

    id : int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(index=True, unique=True)
    is_admin: bool = False
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)
    permissions: list["Permission"] = Relationship(back_populates="users", link_model=PermissionUserLink)

    @classmethod
    def get_model(cls) -> type["User"]:
        """
        Get the model class for the User.

        Returns:
            type: The model class for the User.

        """
        return cls

    @classmethod
    def set_model(cls, model: type["User"]) -> None:
        """
        Set the model class for the User.

        Args:
            model (type): The model class to set.

        """
        pass


class Role(SQLModel, table=True):
    """
    Role model.

    This model represents a role in the system. It is used to manage
    user permissions and access levels.

    Attributes:
        name (str): The name of the role.
    """

    id : int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    users: list[User] = Relationship(back_populates="roles", link_model=UserRoleLink)
    permissions: list["Permission"] = Relationship(back_populates="roles", link_model=PermissionRoleLink)


class Permission(SQLModel, table=True):
    """
    Permission model for actions.

    Attributes:
        action_id (int): The ID of the registered action.
        users (list[User]): List of users with this permission.
        roles (list[Role]): List of roles with this permission.
    """

    id : int | None = Field(default=None, primary_key=True)
    action_id: int | None = Field(default=None, foreign_key="registeredaction.id", index=True, ondelete="CASCADE")
    action: RegisteredAction = Relationship(back_populates="permissions")
    users: list[User] = Relationship(back_populates="permissions", link_model=PermissionUserLink)
    roles: list[Role] = Relationship(back_populates="permissions", link_model=PermissionRoleLink)

    def is_user_allowed(self, user: User) -> bool:
        """
        Check if a user has this permission.

        Args:
            user (User): The user to check.

        Returns:
            bool: True if the user has this permission, False otherwise.
        """
        if user in self.users:
            return True
        for role in user.roles:
            if role in self.roles:
                return True
        return False
