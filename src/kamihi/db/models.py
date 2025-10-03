"""
Internal models for Kamihi.

License:
    MIT
"""

from __future__ import annotations

from typing import Any, ClassVar

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, declared_attr, mapped_column, relationship

Base = declarative_base()


class RegisteredAction(Base):
    """
    Model for registered actions.

    Attributes:
        id (int): Primary key.
        name (str): Name of the action.
        description (str | None): Description of the action.
        permissions (list[Permission]): List of permissions associated with the action.

    """

    __tablename__ = "registeredaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        back_populates="action",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    async def __admin_repr__(self, *args: Any, **kwargs: Any) -> str:  # noqa: ANN401
        """Define the representation of the action in the admin interface."""
        return "/" + self.name


class UserRoleLink(Base):
    """
    Association table for many-to-many relationship between users and roles.

    Attributes:
        user_id (int): Foreign key to the user.
        role_id (int): Foreign key to the role.

    """

    __tablename__ = "userrolelink"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)


class PermissionUserLink(Base):
    """
    Association table for many-to-many relationship between permissions and users.

    Attributes:
        permission_id (int): Foreign key to the permission.
        user_id (int): Foreign key to the user.

    """

    __tablename__ = "permissionuserlink"

    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)


class PermissionRoleLink(Base):
    """
    Association table for many-to-many relationship between permissions and roles.

    Attributes:
        permission_id (int): Foreign key to the permission.
        role_id (int): Foreign key to the role.

    """

    __tablename__ = "permissionrolelink"

    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)


class BaseUser(Base):
    """
    Base class for user models.

    This class should be extended in user code to create a custom user model.

    Attributes:
        id (int): Primary key.
        telegram_id (int): Unique Telegram ID of the user.
        is_admin (bool): Whether the user is an admin.
        roles (list[Role]): List of roles associated with the user.
        permissions (list[Permission]): List of permissions associated with the user.

    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="userrolelink",
        back_populates="users",
    )
    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        secondary="permissionuserlink",
        back_populates="users",
    )

    _active_class: ClassVar[type[BaseUser] | None] = None

    @declared_attr
    def __tablename__(self) -> str:
        """Dynamically set the table name for the user model."""
        return "user"

    def __init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        """Register a custom user model."""
        super().__init_subclass__(**kwargs)

        # Find the real base dynamically
        base = next((b for b in cls.__mro__ if b.__name__ == "BaseUser"), None)
        if base is None or cls.__name__ == "BaseUser":
            return  # don't register the base itself

        if base._active_class is not None:  # noqa: SLF001
            raise RuntimeError("A custom User model is already registered")

        # Disable the default User model if it exists
        if "User" in globals():
            globals()["User"].__table__ = None
            globals()["User"].__mapper__ = None

        base._active_class = cls  # noqa: SLF001

    @classmethod
    def cls(cls) -> type[BaseUser]:
        """Get the active user class."""
        return cls._active_class or globals()["User"]

    def admin_repr(self) -> str:
        """Define the representation of the user in the admin interface."""
        return str(self.telegram_id)

    async def __admin_repr__(self, *args: Any, **kwargs: Any) -> str:  # noqa: ANN401
        """Async representation for admin interface."""
        return self.admin_repr()


class Role(Base):
    """
    Model for roles.

    Attributes:
        id (int): Primary key.
        name (str): Name of the role.
        users (list[User]): List of users associated with the role.
        permissions (list[Permission]): List of permissions associated with the role.

    """

    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True)

    users: Mapped[list["User"]] = relationship(  # noqa: UP037
        "User",
        secondary="userrolelink",
        back_populates="roles",
    )
    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        secondary="permissionrolelink",
        back_populates="roles",
    )

    async def __admin_repr__(self, *args: Any, **kwargs: Any) -> str:  # noqa: ANN401
        """Define the representation of the role in the admin interface."""
        return self.name


class Permission(Base):
    """
    Model for permissions.

    Attributes:
        id (int): Primary key.
        action_id (int | None): Foreign key to the registered action.
        action (RegisteredAction): The registered action associated with the permission.
        users (list[User]): List of users associated with the permission.
        roles (list[Role]): List of roles associated with the permission.

    """

    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_id: Mapped[int | None] = mapped_column(
        ForeignKey("registeredaction.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    action: Mapped[RegisteredAction] = relationship(
        "RegisteredAction",
        back_populates="permissions",
    )
    users: Mapped[list["User"]] = relationship(  # noqa: UP037
        "User",
        secondary="permissionuserlink",
        back_populates="permissions",
    )
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="permissionrolelink",
        back_populates="permissions",
    )

    async def __admin_repr__(self, *args: Any, **kwargs: Any) -> str:  # noqa: ANN401
        """Define the representation of the permission in the admin interface."""
        return f"Permission for /{self.action.name if self.action else 'No Action'}"

    def is_user_allowed(self, user: BaseUser) -> bool:
        """
        Check if a user has this permission.

        Args:
            user (User): The user to check.

        Returns:
            bool: True if the user has this permission, False otherwise.

        """
        if user in self.users:
            return True
        return any(role in self.roles for role in user.roles)
