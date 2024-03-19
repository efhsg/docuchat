from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    Index,
    Enum,
    func,
)
from sqlalchemy.dialects.mysql import LONGBLOB, JSON
from sqlalchemy.orm import declarative_base, relationship, validates, deferred
from sqlalchemy.ext.mutable import MutableDict
import enum
import re

Base = declarative_base()


class Validatable:
    MAX_NAME_LENGTH = 255
    NAME_PATTERN = r"^[a-zA-Z0-9 `~!@#$%^&*()\-_+=\[\]{\}|\\:;\"'<>,\.\?/]+$"

    @validates("name")
    def validate_name(self, key, name):
        if len(name) > self.MAX_NAME_LENGTH:
            raise ValueError(
                f"Name exceeds maximum length of {self.MAX_NAME_LENGTH} characters: {name}"
            )
        if not re.match(self.NAME_PATTERN, name):
            raise ValueError(
                "Invalid name. Allowed characters include letters, digits, and most special characters found on a standard US keyboard. Received: "
                + name
            )
        return name


class Domain(Base, Validatable):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    extracted_texts = relationship(
        "ExtractedText", backref="domain", cascade="all, delete-orphan"
    )


class ExtractedText(Base, Validatable):
    __tablename__ = "extracted_texts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(
        Integer, ForeignKey("domains.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(255), nullable=False)
    type = Column(String(10), nullable=False)
    original_name = Column(String(255), nullable=False)
    text = deferred(Column(LONGBLOB, nullable=False))


class ChunkProcess(Base):
    __tablename__ = "chunk_processes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    extracted_text_id = Column(
        Integer, ForeignKey("extracted_texts.id", ondelete="CASCADE"), nullable=False
    )
    parameters = Column(MutableDict.as_mutable(JSON))
    method = Column(String(50), nullable=False)
    extracted_text = relationship("ExtractedText", backref="chunk_processes")
    embedding_processes = relationship("EmbeddingProcess", backref="chunk_process")


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_process_id = Column(
        Integer, ForeignKey("chunk_processes.id", ondelete="CASCADE"), nullable=False
    )
    index = Column(Integer, nullable=False)
    chunk = deferred(Column(LONGBLOB, nullable=False))
    __table_args__ = (
        UniqueConstraint(
            "chunk_process_id", "index", name="_chunk_process_id_index_uc"
        ),
    )


class EmbeddingProcess(Base, Validatable):
    __tablename__ = "embedding_processes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_process_id = Column(
        Integer, ForeignKey("chunk_processes.id", ondelete="CASCADE"), nullable=False
    )
    method = Column(String(255), nullable=False)
    parameters = Column(MutableDict.as_mutable(JSON), nullable=False)


class Embedding(Base):
    __tablename__ = "embeddings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_id = Column(
        Integer, ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False
    )
    embedding_process_id = Column(
        Integer,
        ForeignKey("embedding_processes.id", ondelete="CASCADE"),
        nullable=False,
    )
    embedding = deferred(Column(LONGBLOB, nullable=False))
    __table_args__ = (
        Index("ix_embeddings_chunk_id", "chunk_id"),
        Index("ix_embeddings_embedding_process_id", "embedding_process_id"),
        UniqueConstraint(
            "chunk_id", "embedding_process_id", name="uix_chunk_id_embedding_process_id"
        ),
    )


class ModelSource(enum.Enum):
    Groq = "Groq"
    OpenAI = "OpenAI"


class ModelCache(Base):
    __tablename__ = "model_cache"
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(Enum(ModelSource), nullable=False)
    model_id = Column(String(255), nullable=False)
    attributes = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("source", "model_id", name="_source_model_id_uc"),
    )
