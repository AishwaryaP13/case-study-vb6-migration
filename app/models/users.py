from typing import Optional
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Level(Base):
    __tablename__ = "Levels"

    level: Mapped[str] = mapped_column("Level", Text, primary_key=True, nullable=False)


class User(Base):
    __tablename__ = "Users"

    username: Mapped[str] = mapped_column("Username", Text, primary_key=True, nullable=False)
    password: Mapped[Optional[str]] = mapped_column("Password", Text)
    fullname: Mapped[Optional[str]] = mapped_column("Fullname", Text)
    level: Mapped[Optional[str]] = mapped_column(
        "Level", Text, ForeignKey("Levels.Level"), nullable=True
    )
