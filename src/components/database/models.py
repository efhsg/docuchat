from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import declarative_base, relationship, validates, deferred
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.mysql import JSON
import re

Base = declarative_base()


class Validatable:
    MAX_NAME_LENGTH = 255
    NAME_PATTERN = r"^[a-zA-Z0-9 .@#$%^&*()_+\[\]\:\\/{}<>!?\-`]+$"

    @validates("name")
    def validate_name(self, key, name):
        if len(name) > self.MAX_NAME_LENGTH:
            raise ValueError(
                f"Name exceeds maximum length of {self.MAX_NAME_LENGTH} characters: {name}"
            )
        if not re.match(self.NAME_PATTERN, name):
            raise ValueError(
                "Invalid name. Allowed characters are letters, digits, spaces, and .@#$%^&*()_+[]/\\\\{}<>!?-:` "
                + name
            )
        return name


class Domain(Base, Validatable):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)


class ExtractedText(Base, Validatable):
    __tablename__ = "extracted_texts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(10), nullable=False)
    original_name = Column(String(255), nullable=False)
    text = deferred(Column(LONGBLOB, nullable=False))
    domain = relationship("Domain", backref="extracted_texts")
    __table_args__ = (
        UniqueConstraint("name", "domain_id", "type", name="_name_domain_id_type_uc"),
    )


class ChunkProcess(Base):
    __tablename__ = "chunk_processes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    extracted_text_id = Column(
        Integer, ForeignKey("extracted_texts.id"), nullable=False
    )
    parameters = Column(MutableDict.as_mutable(JSON))
    method = Column(String(50), nullable=False)
    extracted_text = relationship("ExtractedText", backref="chunk_processes")


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chunk_process_id = Column(Integer, ForeignKey("chunk_processes.id"), nullable=False)
    index = Column(Integer, nullable=False)
    chunk = deferred(Column(LONGBLOB, nullable=False))
    chunk_process = relationship("ChunkProcess", backref="chunks")
    __table_args__ = (
        UniqueConstraint(
            "chunk_process_id", "index", name="_chunk_process_id_index_uc"
        ),
    )
