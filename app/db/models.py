from sqlmodel import Field, SQLModel
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone

# brauche ich?
class DeviceType(SQLModel, table=True):
	__tablename__ = "device_type"
	id: int = Field(default=None, primary_key=True)
	name: str = Field(index=True, nullable=False, unique=True)
	description: str = Field(nullable=True)
	created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)

# Brauche ich?
class DeviceDriver(SQLModel, table=True):
	__tablename__ = "device_driver"
	id: int = Field(default=None, primary_key=True)
	name: str = Field(index=True, nullable=False, unique=True)
	description: str = Field(nullable=True)
	created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)

class Device(SQLModel, table=True):
	id: int = Field(default=None, primary_key=True)
	name: str = Field(nullable=True,)
	device_host: str = Field(index=True, nullable=False, unique=True)
	device_type: str = Field(foreign_key="device_type.id", default=None, nullable=True)
	device_driver: str = Field(foreign_key="device_driver.id", nullable=True)
	created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)

class User(SQLModel, table=True):
	id: int = Field(default=None, primary_key=True)
	username: str = Field(index=True, nullable=False, unique=True)
	password: str = Field(nullable=False)
	email: str = Field(index=True, nullable=True, unique=True)
	firstname: str = Field(nullable=True)
	lastname: str = Field(nullable=True)
	created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)
	updated_at: datetime = Field(
        sa_column=Column(
            DateTime(),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False
        )
    )

class KeyType(SQLModel, table=True):
	__tablename__ = "key_type"
	id: int = Field(default=None, primary_key=True)
	name: str = Field(index=True, nullable=False, unique=True)
	description: str = Field(nullable=True)
	created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)

class Key(SQLModel, table=True):
	id: int = Field(default=None, primary_key=True)
	key: str = Field(index=True, nullable=False, unique=True)
	key_type: str = Field(foreign_key="key_type.id", nullable=False)
	user_id: int = Field(foreign_key="user.id", nullable=False)
	created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)
	updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(),
            onupdate=lambda: datetime.now(),
            nullable=False
        )
    )
	expires_at: datetime = Field(nullable=True)

# class Automation_temparute(SQLModel, table=True):
# 	id: int = Field(default=None, primary_key=True)

class ApiKey(SQLModel, table=True):
	id: int = Field(default=None, primary_key=True)
	key: str = Field(index=True, nullable=False, unique=True)
	user_id: int = Field(foreign_key="user.id", nullable=False)
	created_at: datetime = Field(default_factory=lambda: datetime.now(), nullable=False)
	expires_at: datetime = Field(nullable=True)
