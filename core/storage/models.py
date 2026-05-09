from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Enum, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class JobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Severity(enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    domain = Column(String(255), unique=True, nullable=False)
    organization = Column(String(255))
    ip_address = Column(String(45))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    scans = relationship("ScanJob", back_populates="target")
    assets = relationship("Asset", back_populates="target")

class ScanJob(Base):
    __tablename__ = 'scan_jobs'
    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey('targets.id'))
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    progress = Column(Float, default=0.0)
    options = Column(JSON) # Store scan flags like --full-recon
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    results_summary = Column(Text) # AI summary
    
    target = relationship("Target", back_populates="scans")
    vulnerabilities = relationship("Vulnerability", back_populates="scan_job")
    findings = relationship("Finding", back_populates="scan_job")
    logs = relationship("ScanLog", back_populates="scan_job")

class Asset(Base):
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    target_id = Column(Integer, ForeignKey('targets.id'))
    type = Column(String(50)) # domain, ip, service, bucket
    value = Column(String(255))
    metadata_json = Column(JSON)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    target = relationship("Target", back_populates="assets")
    technologies = relationship("Technology", back_populates="asset")

class Technology(Base):
    __tablename__ = 'technologies'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    name = Column(String(100))
    version = Column(String(50))
    category = Column(String(100))
    icon = Column(String(255))
    website = Column(String(255))
    
    asset = relationship("Asset", back_populates="technologies")
    cves = relationship("CVE", back_populates="technology")

class CVE(Base):
    __tablename__ = 'cves'
    id = Column(Integer, primary_key=True)
    technology_id = Column(Integer, ForeignKey('technologies.id'))
    cve_id = Column(String(50)) # e.g., CVE-2023-1234
    cvss_score = Column(Float)
    severity = Column(String(20))
    description = Column(Text)
    exploit_available = Column(Boolean, default=False)
    references = Column(JSON)
    
    technology = relationship("Technology", back_populates="cves")

class Finding(Base):
    """Real tool outputs stored as findings before AI analysis"""
    __tablename__ = 'findings'
    id = Column(Integer, primary_key=True)
    scan_job_id = Column(Integer, ForeignKey('scan_jobs.id'))
    tool = Column(String(50)) # nuclei, nmap, etc.
    type = Column(String(100)) # e.g., open-port, sub-domain, vuln
    data = Column(JSON)
    evidence = Column(Text)
    severity = Column(Enum(Severity))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    scan_job = relationship("ScanJob", back_populates="findings")

class Vulnerability(Base):
    """Verified or highly probable vulnerabilities, often enriched by AI"""
    __tablename__ = 'vulnerabilities'
    id = Column(Integer, primary_key=True)
    scan_job_id = Column(Integer, ForeignKey('scan_jobs.id'))
    name = Column(String(255))
    description = Column(Text)
    severity = Column(Enum(Severity))
    cvss_score = Column(Float)
    cve_id = Column(String(50))
    cwe_id = Column(String(50))
    owasp_category = Column(String(100))
    remediation = Column(Text)
    evidence = Column(Text)
    affected_component = Column(String(255))
    is_false_positive = Column(Boolean, default=False)
    
    scan_job = relationship("ScanJob", back_populates="vulnerabilities")

class ScanLog(Base):
    __tablename__ = 'scan_logs'
    id = Column(Integer, primary_key=True)
    scan_job_id = Column(Integer, ForeignKey('scan_jobs.id'))
    level = Column(String(20))
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    scan_job = relationship("ScanJob", back_populates="logs")

class Report(Base):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    scan_job_id = Column(Integer, ForeignKey('scan_jobs.id'))
    file_path = Column(String(255))
    report_type = Column(String(20)) # PDF, HTML, JSON
    created_at = Column(DateTime, default=datetime.utcnow)
