"""
Internal models for Kamihi.

License:
    MIT
"""
from __future__ import annotations

from typing import List, ClassVar, Optional, Type

from sqlalchemy import ForeignKey, Boolean, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column, declared_attr

Base = declarative_base()


class RegisteredAction(Base):
    __tablename__ = "registeredaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)

    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        back_populates="action",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    async def __admin_repr__(self, *args, **kwargs) -> str:
        return "/" + self.name


class UserRoleLink(Base):
    __tablename__ = "userrolelink"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)


class PermissionUserLink(Base):
    __tablename__ = "permissionuserlink"

    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)


class PermissionRoleLink(Base):
    __tablename__ = "permissionrolelink"

    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)


class BaseUser(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="userrolelink",
        back_populates="users",
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="permissionuserlink",
        back_populates="users",
    )

    _active_class: ClassVar[Optional[Type["BaseUser"]]] = None

    @declared_attr
    def __tablename__(cls):
        return "user"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # Find the real base dynamically
        base = next((b for b in cls.__mro__ if b.__name__ == "BaseUser"), None)
        if base is None or cls.__name__ == "BaseUser":
            return  # don't register the base itself

        if base._active_class is not None:
            raise RuntimeError("A custom User model is already registered")

        # Disable the default User model if it exists
        if "User" in globals():
            globals()["User"].__table__ = None
            globals()["User"].__mapper__ = None

        base._active_class = cls


    @classmethod
    def cls(cls):
        return cls._active_class or globals()["User"]

    def admin_repr(self) -> str:
        return str(self.telegram_id)

    async def __admin_repr__(self, *args, **kwargs) -> str:
        return self.admin_repr()


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, index=True, unique=True)

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="userrolelink",
        back_populates="roles",
    )
    permissions: Mapped[List["Permission"]] = relationship(
        "Permission",
        secondary="permissionrolelink",
        back_populates="roles",
    )

    async def __admin_repr__(self, *args, **kwargs) -> str:
        return self.name


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action_id: Mapped[int | None] = mapped_column(
        ForeignKey("registeredaction.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )

    action: Mapped["RegisteredAction"] = relationship(
        "RegisteredAction",
        back_populates="permissions",
    )
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary="permissionuserlink",
        back_populates="permissions",
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="permissionrolelink",
        back_populates="permissions",
    )

    async def __admin_repr__(self, *args, **kwargs) -> str:
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
        for role in user.roles:
            if role in self.roles:
                return True
        return False
