from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Table, ForeignKey
from sqlalchemy.orm import relationship
from config.database import FastModel


class User(FastModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(256), nullable=False, unique=True)
    username = Column(String(25))
    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)

    password = Column(String, nullable=False)
    totp_secret = Column(String)

    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # TODO : Add RBAC to the user model
    # groups
    # permissions
    
    # get_user_permissions
    # get_group_permissions
    # has_perm


groups_permissions = Table(
    "groups_permissions",
    FastModel.metadata,
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
    Column("group_id", ForeignKey("groups.id"), primary_key=True)
)


class Permission(FastModel):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(256))

    groups = relationship("Group", secondary=groups_permissions, back_populates="permissions")

    # TODO: Implement permission model

class Group(FastModel):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)

    permissions = relationship("Permission", secondary=groups_permissions, back_populates="groups")