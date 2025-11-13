"""
Database Models for DaycareMoments
Core 4 tables: organizations, users, persons (children), photos
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate UUID for primary keys"""
    return str(uuid.uuid4())


class Organization(Base):
    """Organization (Daycare) model"""
    __tablename__ = 'organizations'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    persons = relationship("Person", back_populates="organization")
    photos = relationship("Photo", back_populates="organization")


class User(Base):
    """User model - staff and parents"""
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'parent', 'staff', 'admin'
    organization_id = Column(String, ForeignKey('organizations.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    uploaded_photos = relationship("Photo", back_populates="uploader", foreign_keys="Photo.uploaded_by")


class Person(Base):
    """Person (Child) model - persons enrolled in daycare"""
    __tablename__ = 'persons'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    face_encodings = Column(JSON, default=[])  # List of face encoding arrays for recognition
    organization_id = Column(String, ForeignKey('organizations.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="persons")
    photos = relationship("Photo", back_populates="person")


class Photo(Base):
    """Photo model - stores photo metadata and AI descriptions"""
    __tablename__ = 'photos'

    id = Column(String, primary_key=True, default=generate_uuid)
    url = Column(String, nullable=False)  # Storage URL or local path
    person_id = Column(String, ForeignKey('persons.id'))
    ai_description = Column(Text)  # AI-generated activity description
    uploaded_by = Column(String, ForeignKey('users.id'))
    organization_id = Column(String, ForeignKey('organizations.id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    person = relationship("Person", back_populates="photos")
    uploader = relationship("User", back_populates="uploaded_photos", foreign_keys=[uploaded_by])
    organization = relationship("Organization", back_populates="photos")
