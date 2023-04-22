from datetime import datetime as dt

import shortuuid
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship

Base = declarative_base()
metadata = Base.metadata


class BaseModel(Base):
    __abstract__ = True
    id = Column(
        String(22),
        primary_key=True,
        default=shortuuid.uuid,
        unique=True,
        nullable=False,
    )
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


# using events, fields are automatically set whenever an object is inserted or updated
# using the ORM, without requiring you to explicitly call a custom save method.
@event.listens_for(Session, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = dt.utcnow()
    target.updated_at = dt.utcnow()


@event.listens_for(Session, "before_update")
def set_updated_at(mapper, connection, target):
    target.updated_at = dt.utcnow()


class Document(BaseModel):
    __tablename__ = "documents"

    url = Column(Text, nullable=False, unique=True)

    sections = relationship("Section", back_populates="document")


class Section(BaseModel):
    __tablename__ = "sections"

    content = Column(Text, nullable=False)
    document_id = Column(String(22), ForeignKey("documents.id"), nullable=False)

    document = relationship("Document", back_populates="sections")
