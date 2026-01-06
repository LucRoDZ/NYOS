from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db import Base


class DataType(str, enum.Enum):
    BATCH = "batch"
    QC = "qc"
    COMPLAINT = "complaint"
    CAPA = "capa"
    EQUIPMENT = "equipment"
    ENVIRONMENTAL = "environmental"
    RAW_MATERIAL = "raw_material"
    STABILITY = "stability"


class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(50), unique=True, index=True)
    product_name = Column(String(100))
    manufacturing_date = Column(DateTime)
    machine = Column(String(50))
    operator = Column(String(50))
    compression_force = Column(Float)
    hardness = Column(Float)
    weight = Column(Float)
    thickness = Column(Float)
    yield_percent = Column(Float)
    status = Column(String(20), default="released")
    created_at = Column(DateTime, default=datetime.utcnow)


class QCResult(Base):
    __tablename__ = "qc_results"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(50), ForeignKey("batches.batch_id"), index=True)
    test_date = Column(DateTime)
    dissolution = Column(Float)
    assay = Column(Float)
    hardness = Column(Float)
    friability = Column(Float)
    disintegration = Column(Float)
    uniformity = Column(Float)
    result = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)


class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(50), unique=True, index=True)
    date = Column(DateTime)
    batch_id = Column(String(50))
    category = Column(String(50))
    severity = Column(String(20))
    description = Column(Text)
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)


class CAPA(Base):
    __tablename__ = "capas"
    id = Column(Integer, primary_key=True, index=True)
    capa_id = Column(String(50), unique=True, index=True)
    date = Column(DateTime)
    type = Column(String(20))
    source = Column(String(50))
    description = Column(Text)
    root_cause = Column(Text)
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)


class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(50), index=True)
    name = Column(String(100))
    calibration_date = Column(DateTime)
    next_calibration = Column(DateTime)
    status = Column(String(20))
    parameter = Column(String(50))
    deviation = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="Nouvelle conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship(
        "ChatMessage", back_populates="conversation", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), index=True)
    role = Column(String(20))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", back_populates="messages")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    data_type = Column(String(50))
    records_count = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
