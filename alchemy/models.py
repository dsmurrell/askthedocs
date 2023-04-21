# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
metadata = Base.metadata


class BaseModel(Base):
    __abstract__ = True
    id = Column(String(255), primary_key=True)
    created_at = Column(DateTime(True), nullable=False)
    updated_at = Column(DateTime(True), nullable=False)


class Document(BaseModel):
    __tablename__ = "documents"

    url = Column(Text, nullable=False, unique=True)

    sections = relationship("Section", back_populates="document")


class Section(BaseModel):
    __tablename__ = "sections"

    content = Column(Text, nullable=False)
    document_id = Column(String(255), ForeignKey("documents.id"), nullable=False)

    document = relationship("Document", back_populates="sections")
