from datetime import datetime as dt

import shortuuid
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column, relationship

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
    created_at = Column(DateTime(True), nullable=False, default=dt.utcnow)
    updated_at = Column(
        DateTime(True), nullable=False, default=dt.utcnow, onupdate=dt.utcnow
    )

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class Document(BaseModel):
    __tablename__ = "documents"

    url = Column(Text, nullable=False, unique=True)
    # notion page id for example
    external_id = Column(String(64), nullable=True, unique=True)
    hash = Column(String(64), nullable=False, unique=True)
    title = Column(Text, nullable=True)
    text = Column(Text)
    root_node = relationship("Node", uselist=False, back_populates="document")


class Node(BaseModel):
    __tablename__ = "nodes"

    title = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    depth_level = Column(Integer, nullable=False, default=0)
    parent_id = Column(String(22), ForeignKey("nodes.id"), nullable=True)
    document_id = Column(String(22), ForeignKey("documents.id"), nullable=True)

    parent = relationship("Node", remote_side=lambda: Node.id, backref="children")
    document = relationship("Document", back_populates="root_node")


# TODO: Remove below when node approach is implemented
class Section(BaseModel):
    __tablename__ = "sections"

    text = Column(Text, nullable=False)
    embedding = mapped_column(Vector(1536))
    hash = Column(String(64), nullable=False, unique=True)
    number = Column(Integer, nullable=False)
    document_id = Column(String(22), ForeignKey("documents.id"), nullable=False)

    document = relationship("Document", back_populates="sections")


# old document model
# class Document(BaseModel):
#     __tablename__ = "documents"

#     url = Column(Text, nullable=False, unique=True)
#     hash = Column(String(64), nullable=False, unique=True)
#     title = Column(Text, nullable=True)
#     text = Column(Text)
#     sections = relationship("Section", back_populates="document")

# old node model
# class Node(BaseModel):
#     __tablename__ = "nodes"

#     title = Column(Text, nullable=True)
#     text = Column(Text)
#     depth_level = Column(Integer, nullable=False)
#     parent_id = Column(String(22), ForeignKey("nodes.id"), nullable=True)

#     parent = relationship("Node", remote_side=lambda: Node.id, backref="children")
