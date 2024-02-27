from sqlalchemy import Column, Integer, String, UniqueConstraint, ForeignKey
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import declarative_base, validates, relationship, deferred
import re

Base = declarative_base()


class Validatable:
    MAX_NAME_LENGTH = 10
    NAME_PATTERN = r"^[a-zA-Z0-9 .@#$%^&*()_+\[\]/{}<>!?-]+$"

    @validates("name")
    def validate_name(self, key, name):
        if len(name) > self.MAX_NAME_LENGTH:
            raise ValueError(
                f"Name exceeds maximum length of {self.MAX_NAME_LENGTH} characters: {name}"
            )
        if not re.match(self.NAME_PATTERN, name):
            raise ValueError(
                "Invalid name. Allowed characters are letters, digits, spaces, and .@#$%^&*()_+[]/{}/<>!?-: "
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
