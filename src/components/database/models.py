from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import deferred
import re

Base = declarative_base()


class Domain(Base):
    MAX_DOMAIN_NAME_LENGTH = 255
    DOMAIN_NAME_PATTERN = r"^[a-zA-Z0-9 .@#$%^&*()_+\[\]/{}<>!?-]+$"

    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(MAX_DOMAIN_NAME_LENGTH), unique=True, nullable=False)

    def __init__(self, name: str):
        if not re.match(self.DOMAIN_NAME_PATTERN, name):
            raise ValueError("Invalid domain name")
        self.name = name


class ExtractedText(Base):
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
