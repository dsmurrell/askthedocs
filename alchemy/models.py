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
    external_id = Column(String(64), nullable=False, unique=True)
    hash = Column(String(64), nullable=False, unique=True)
    title = Column(Text)
    text = Column(Text)
    text_no_html = Column(Text)
    root_node = relationship("Node", uselist=False, back_populates="document")


class Node(BaseModel):
    __tablename__ = "nodes"

    title = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    text_cleaned = Column(Text)
    text_processed = Column(Text)
    embedding = mapped_column(Vector(1536))
    hash = Column(String(64), nullable=False, unique=True)
    text_length = Column(Integer, nullable=False)
    depth_level = Column(Integer, nullable=False, default=0)
    parent_id = Column(String(22), ForeignKey("nodes.id"))
    document_id = Column(String(22), ForeignKey("documents.id"))

    parent = relationship("Node", remote_side=lambda: Node.id, backref="children")
    document = relationship("Document", back_populates="root_node")


class User(BaseModel):
    __tablename__ = "users"
    username = Column(String(100), nullable=False, unique=True)
    platform = Column(String(50), nullable=False)  # Discord, Telegram, Slack, etc.

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Conversation(BaseModel):
    __tablename__ = "conversations"
    user_id = Column(String(22), ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="conversations")

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id})>"


class Message(BaseModel):
    __tablename__ = "messages"
    conversation_id = Column(String(22), ForeignKey("conversations.id"), nullable=False)
    sender = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)

    conversation = relationship("Conversation", backref="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, sender={self.sender}, content={self.content})>"
