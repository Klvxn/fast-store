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

    # TODO remove `is_verified` check it from `is_active`: if id active means that user is verified too.
    is_verified = Column(Boolean, default=False)

    is_superuser = Column(Boolean, default=False)

    # TODO remove this too, for now the `is_superuser` is ok.
    is_staff = Column(Boolean, default=False)

    password = Column(String, nullable=False)

    # TODO rename this to `otp`
    totp_secret = Column(String)

    last_login = Column(DateTime, nullable=True)

    # TODO rename field to `date_joined`
    created_at = Column(DateTime, server_default=func.now())

    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # TODO : Add RBAC to the user model
    # groups
    # permissions

    # get_user_permissions
    # get_group_permissions
    # has_perm


# TODO Ask, ContentType what is this?
class ContentType(FastModel):
    __tablename__ = "content_types"
    id = Column(Integer, primary_key=True)
    app_label = Column(String(100))
    model = Column(String(100))
    permissions = relationship("Permission", back_populates="content_type", cascade="all, delete-orphan")


# TODO Ask, ContentType what is this?
groups_permissions = Table(
    "groups_permissions",
    FastModel.metadata,
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
    Column("group_id", ForeignKey("groups.id"), primary_key=True)
)


# TODO we need to add class and check permission for an action: user.has_add_product() -> boolean
class Permission(FastModel):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String(256))

    codename = Column(String(100))

    content_type_id = Column(Integer, ForeignKey("content_types.id"))
    content_type = relationship("ContentType", back_populates="permissions")
    groups = relationship("Group", secondary=groups_permissions, back_populates="permissions")


# TODO, remove, don't need to it, permissions is ok.
class Group(FastModel):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)

    permissions = relationship("Permission", secondary=groups_permissions, back_populates="groups")
