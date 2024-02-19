from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)


class ExtractedText(Base):
    __tablename__ = "extracted_texts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    text = Column(LONGBLOB, nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    domain = relationship("Domain", backref="extracted_texts")
    __table_args__ = (UniqueConstraint("name", "domain_id", name="_name_domain_id_uc"),)
