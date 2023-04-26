from datetime import datetime as dt
from typing import Optional

import shortuuid
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlmodel import Field, Relationship, SQLModel


class BaseModel(SQLModel, table=False):
    id: str = Field(
        default_factory=shortuuid.uuid,
        primary_key=True,
        unique=True,
        nullable=False,
        sa_column=String(22),
    )
    created_at: dt = Field(
        default_factory=dt.utcnow, nullable=False, sa_column=DateTime(True)
    )
    updated_at: dt = Field(
        default_factory=dt.utcnow,
        nullable=False,
        sa_column=DateTime(True),
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    def before_update(self):
        self.updated_at = dt.utcnow()


class Document(BaseModel):
    __tablename__ = "documents"

    url: str = Field(nullable=False, unique=True, sa_column=Text)
    hash: str = Field(nullable=False, unique=True, sa_column=String(64))
    title: Optional[str] = Field(nullable=True, sa_column=Text)
    sections: list["Section"] = Relationship(back_populates="document")


class Section(BaseModel):
    __tablename__ = "sections"

    text: str = Field(nullable=False, sa_column=Text)
    hash: str = Field(nullable=False, unique=True, sa_column=String(64))
    number: int = Field(nullable=False, sa_column=Integer)
    document_id: str = Field(
        ForeignKey("documents.id"), nullable=False, sa_column=String(22)
    )

    document: Document = Relationship(back_populates="sections")
    document: Document = Relationship(back_populates="sections")
