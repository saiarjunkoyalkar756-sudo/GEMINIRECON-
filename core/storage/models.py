from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    domain = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    scans = relationship("Scan", back_populates="target")

class Scan(Base):
    __tablename__ = 'scans'
    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey('targets.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    plan = Column(Text)
    recon_data = Column(Text)
    analysis = Column(Text)
    risk_assessment = Column(Text)
    target = relationship("Target", back_populates="scans")

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey('targets.id'))
    type = Column(String(50)) # subdomain, ip, technology, etc.
    value = Column(Text)
    metadata_json = Column(Text)
    discovered_at = Column(DateTime, default=datetime.utcnow)
