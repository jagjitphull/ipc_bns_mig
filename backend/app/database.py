"""
Database setup and models for IPC-BNS mapping and case law
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

# Association table for many-to-many relationship between sections and cases
section_cases = Table('section_cases', Base.metadata,
    Column('section_id', Integer, ForeignKey('ipc_bns_mapping.id')),
    Column('case_id', Integer, ForeignKey('landmark_cases.id'))
)

class IPCBNSMapping(Base):
    __tablename__ = 'ipc_bns_mapping'

    id = Column(Integer, primary_key=True)
    ipc_section = Column(String(50), nullable=False, index=True)
    ipc_description = Column(Text, nullable=False)
    ipc_text = Column(Text, nullable=False)

    bns_section = Column(String(50), nullable=True, index=True)
    bns_description = Column(Text, nullable=True)
    bns_text = Column(Text, nullable=True)

    # Doctrinal changes
    has_changes = Column(Boolean, default=False)
    change_type = Column(String(100), nullable=True)  # 'substantive', 'procedural', 'linguistic', 'none', 'repealed'
    change_summary = Column(Text, nullable=True)
    change_details = Column(Text, nullable=True)  # JSON format

    # Metadata
    category = Column(String(100), nullable=True)  # e.g., 'Offences against State', 'Murder', etc.
    punishment = Column(Text, nullable=True)

    # Relationships
    cases = relationship('LandmarkCase', secondary=section_cases, back_populates='sections')

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LandmarkCase(Base):
    __tablename__ = 'landmark_cases'

    id = Column(Integer, primary_key=True)
    case_name = Column(String(500), nullable=False, index=True)
    citation = Column(String(200), nullable=False)
    court = Column(String(200), nullable=False)  # Supreme Court, High Court, etc.

    year = Column(Integer, nullable=False, index=True)
    judges = Column(Text, nullable=True)  # JSON array

    # Case details
    facts = Column(Text, nullable=False)
    legal_issues = Column(Text, nullable=False)
    judgment_summary = Column(Text, nullable=False)
    ratio_decidendi = Column(Text, nullable=False)  # Binding principle
    obiter_dicta = Column(Text, nullable=True)  # Non-binding observations

    # Full text
    full_text = Column(Text, nullable=True)

    # Relevance to BNS transition
    validity_status = Column(String(50), default='valid')  # 'valid', 'questionable', 'invalid', 'requires_review'
    validity_reasoning = Column(Text, nullable=True)

    # Relationships
    sections = relationship('IPCBNSMapping', secondary=section_cases, back_populates='cases')

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AnalysisHistory(Base):
    __tablename__ = 'analysis_history'

    id = Column(Integer, primary_key=True)
    query = Column(Text, nullable=False)
    ipc_sections = Column(Text, nullable=True)  # JSON array
    bns_sections = Column(Text, nullable=True)  # JSON array
    cases_retrieved = Column(Text, nullable=True)  # JSON array

    memo_generated = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


# Database initialization
def init_db(db_path="sqlite:///./legal_reasoning.db"):
    engine = create_engine(db_path, echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return engine, SessionLocal


def get_db():
    engine, SessionLocal = init_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
