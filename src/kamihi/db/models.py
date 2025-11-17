"""
Internal models for Kamihi.

License:
    MIT
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, declarative_base, declared_attr, mapped_column, relationship

Base = declarative_base()


class BaseModel(Base):
    """
    Base model with common attributes.

    Attributes:
        id (int): Primary key.
        created_at (datetime): Timestamp of creation.
        updated_at (datetime): Timestamp of last update.

    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BaseUuidModel(BaseModel):
    """
    Base model with UUID primary key.

    Attributes:
        id (str): Primary key (UUID).

    """

    __abstract__ = True

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class RegisteredAction(BaseModel):
    """
    Model for registered actions.

    Attributes:
        id (int): Primary key.
        name (str): Name of the action.
        description (str | None): Description of the action.
        permissions (list[Permission]): List of permissions associated with the action.

    """

    __tablename__ = "registeredaction"

    name: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        back_populates="action",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    jobs: Mapped[list[Job]] = relationship(
        "Job",
        back_populates="action",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    async def __admin_repr__(self, *args: Any, **kwargs: Any) -> str:
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


class JobUserLink(Base):
    """
    Association table for many-to-many relationship between jobs and users.

    Attributes:
        job_id (str): Foreign key to the job.
        user_id (int): Foreign key to the user.

    """

    __tablename__ = "jobuserlink"

    job_id: Mapped[str] = mapped_column(ForeignKey("job.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)


class JobRoleLink(Base):
    """
    Association table for many-to-many relationship between jobs and roles.

    Attributes:
        job_id (str): Foreign key to the job.
        role_id (int): Foreign key to the role.

    """

    __tablename__ = "jobrolelink"

    job_id: Mapped[str] = mapped_column(ForeignKey("job.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)


class BaseUser(BaseModel):
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
    jobs: Mapped[list[Job]] = relationship(
        "Job",
        secondary="jobuserlink",
        back_populates="users",
    )

    _active_class: ClassVar[type[BaseUser] | None] = None

    @declared_attr
    def __tablename__(self) -> str:
        """Dynamically set the table name for the user model."""
        return "user"

    def __init_subclass__(cls, **kwargs: Any) -> None:
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

    async def __admin_repr__(self, *args: Any, **kwargs: Any) -> str:
        """Async representation for admin interface."""
        return self.admin_repr()


class Role(BaseModel):
    """
    Model for roles.

    Attributes:
        id (int): Primary key.
        name (str): Name of the role.
        users (list[User]): List of users associated with the role.
        permissions (list[Permission]): List of permissions associated with the role.

    """

    __tablename__ = "role"

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
    jobs: Mapped[list[Job]] = relationship(
        "Job",
        secondary="jobrolelink",
        back_populates="roles",
    )

    async def __admin_repr__(self, *args: Any, **kwargs: Any) -> str:
        """Define the representation of the role in the admin interface."""
        return self.name


class Permission(BaseModel):
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

    async def __admin_repr__(self, *args: Any, **kwargs: Any) -> str:
        """Define the representation of the permission in the admin interface."""
        return f"Permission for /{self.action.name if self.action else 'No Action'}"

    @property
    def effective_users(self) -> list[BaseUser]:
        """
        Get the list of users who have this permission, either directly or through roles.

        Returns:
            list[User]: List of users with this permission.

        """
        users_set = set(self.users)
        for role in self.roles:
            users_set.update(role.users)
        return list(users_set)

    def is_user_allowed(self, user: BaseUser) -> bool:
        """
        Check if a user has this permission.

        Args:
            user (User): The user to check.

        Returns:
            bool: True if the user has this permission, False otherwise.

        """
        return user in self.effective_users


class Job(BaseUuidModel):
    """
    Model for scheduled jobs.

    Attributes:
        id (int): Primary key.
        action_id (int): Foreign key to the registered action.
        action (RegisteredAction): The registered action associated with the job.
        cron_expression (str): Cron expression defining the job schedule.
        enabled (bool): Whether the job is active.
        args (dict): Arguments to pass to the job when executed.
        users (list[User]): List of users associated with the job.

    """

    __tablename__ = "job"

    action_id: Mapped[int] = mapped_column(
        ForeignKey("registeredaction.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    action: Mapped[RegisteredAction] = relationship("RegisteredAction")

    cron_expression: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    per_user: Mapped[bool] = mapped_column(Boolean, default=False)
    args: Mapped[JSON] = mapped_column(JSON, default=lambda: {})

    users: Mapped[list["User"]] = relationship(  # noqa: UP037
        "User",
        secondary="jobuserlink",
        back_populates="jobs",
    )

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="jobrolelink",
        back_populates="jobs",
    )

    @property
    def effective_users(self) -> list[BaseUser]:
        """
        Get the list of users associated with this job, either directly or through roles.

        Returns:
            list[User]: List of users associated with this job.

        """
        users_set = set(self.users)
        for role in self.roles:
            users_set.update(role.users)
        return list(users_set)

    async def __admin_repr__(self, *args: Any, **kwargs: Any) -> str:
        """Define the representation of the job in the admin interface."""
        status = "Enabled" if self.enabled else "Disabled"
        return f"Job for /{self.action.name} ({status})"


class Pages(BaseUuidModel):
    """
    Model for pages in a paginated media type.

    Attributes:
        id (int): Primary key.

    """

    __tablename__ = "page"

    pages: Mapped[list[str]] = mapped_column(JSON, default=lambda: [])

    @property
    def len(self) -> int:
        """Get the number of pages."""
        return len(self.pages)
