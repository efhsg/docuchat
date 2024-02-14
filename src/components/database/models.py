from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGBLOB

Base = declarative_base()


class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)


class ExtractedText(Base):
    __tablename__ = "extracted_texts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    text = Column(LONGBLOB, nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False, default=1)
    domain = relationship("Domain", backref="extracted_texts")
