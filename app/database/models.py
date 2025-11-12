"""
Database Models for DaycareMoments
Using SQLAlchemy ORM for database-agnostic code
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text,
    ForeignKey, Table, JSON, LargeBinary, Date, Time, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()


def generate_uuid():
    """Generate UUID for primary keys"""
    return str(uuid.uuid4())


# Association table for parent-children many-to-many relationship
parent_children = Table(
    'parent_children',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('child_id', String, ForeignKey('children.id'), primary_key=True)
)


class UserRole(enum.Enum):
    """User roles"""
    PARENT = "parent"
    STAFF = "staff"
    ADMIN = "admin"


class PhotoStatus(enum.Enum):
    """Photo status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class NotificationType(enum.Enum):
    """Notification types"""
    NEW_PHOTO = "new_photo"
    DAILY_SUMMARY = "daily_summary"
    ANNOUNCEMENT = "announcement"
    ALERT = "alert"
    SYSTEM = "system"


class SubscriptionPlan(enum.Enum):
    """Subscription plans"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"


class Daycare(Base):
    """Daycare model"""
    __tablename__ = 'daycares'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    address = Column(Text)
    email = Column(String)
    phone = Column(String)
    license_number = Column(String, unique=True)
    logo = Column(String)  # URL to logo
    settings = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    timezone = Column(String, default='America/New_York')

    # Google Drive storage management (for service account mode)
    google_drive_folder_id = Column(String)  # Root folder ID for this daycare
    storage_quota_mb = Column(Integer, default=5000)  # 5GB default quota
    storage_used_mb = Column(Integer, default=0)  # Current usage in MB

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="daycare")
    children = relationship("Child", back_populates="daycare")
    photos = relationship("Photo", back_populates="daycare")
    activities = relationship("Activity", back_populates="daycare")
    subscription = relationship("Subscription", back_populates="daycare", uselist=False)


class User(Base):
    """User model"""
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    phone = Column(String)
    profile_photo = Column(String)
    notification_preferences = Column(JSON, default={})
    daycare_id = Column(String, ForeignKey('daycares.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    daycare = relationship("Daycare", back_populates="users")
    children = relationship("Child", secondary=parent_children, back_populates="parents")
    uploaded_photos = relationship("Photo", back_populates="uploader", foreign_keys="Photo.uploaded_by")
    notifications = relationship("Notification", back_populates="user")


class Child(Base):
    """Child model"""
    __tablename__ = 'children'

    id = Column(String, primary_key=True, default=generate_uuid)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String)
    profile_photo = Column(String)
    face_encodings = Column(JSON, default=[])  # List of face encodings for recognition (multiple training photos)
    training_photo_count = Column(Integer, default=0)  # Number of photos used for training
    allergies = Column(Text)
    medical_notes = Column(Text)
    emergency_contact = Column(JSON)
    parent_id = Column(String, ForeignKey('users.id'))  # Primary parent
    daycare_id = Column(String, ForeignKey('daycares.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    daycare = relationship("Daycare", back_populates="children")
    parents = relationship("User", secondary=parent_children, back_populates="children")
    photos = relationship("Photo", back_populates="child")
    activities = relationship("Activity", back_populates="child")


class Activity(Base):
    """Activity log model - records individual child activities"""
    __tablename__ = 'activities'

    id = Column(String, primary_key=True, default=generate_uuid)
    child_id = Column(String, ForeignKey('children.id'), nullable=False)
    daycare_id = Column(String, ForeignKey('daycares.id'), nullable=False)
    staff_id = Column(String, ForeignKey('users.id'))

    activity_type = Column(String, nullable=False)  # meal, nap, play, learning, outdoor, art, diaper change, other
    activity_time = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer)
    notes = Column(Text)
    mood = Column(String)  # emoji or text describing child's mood

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    child = relationship("Child", back_populates="activities")
    daycare = relationship("Daycare", back_populates="activities")
    staff = relationship("User", foreign_keys=[staff_id])
    photos = relationship("Photo", back_populates="activity")


class Photo(Base):
    """Photo model"""
    __tablename__ = 'photos'

    id = Column(String, primary_key=True, default=generate_uuid)
    file_name = Column(String, nullable=False)
    original_file_name = Column(String)
    url = Column(String, nullable=False)
    thumbnail_url = Column(String)
    file_size = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    mime_type = Column(String)
    caption = Column(Text)
    ai_generated_description = Column(Text)  # AI-generated activity description
    tags = Column(JSON, default=[])
    detected_faces = Column(JSON, default=[])  # List of detected face locations
    face_recognition_complete = Column(Boolean, default=False)
    auto_tagged = Column(Boolean, default=False)  # Whether child was auto-tagged by AI
    location = Column(String)
    captured_at = Column(DateTime, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    child_id = Column(String, ForeignKey('children.id'))
    activity_id = Column(String, ForeignKey('activities.id'))
    uploaded_by = Column(String, ForeignKey('users.id'))
    daycare_id = Column(String, ForeignKey('daycares.id'), nullable=False)

    status = Column(Enum(PhotoStatus), default=PhotoStatus.PENDING)
    approved_by = Column(String, ForeignKey('users.id'))
    approved_at = Column(DateTime)

    photo_metadata = Column(JSON, default={})
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    child = relationship("Child", back_populates="photos", foreign_keys=[child_id])
    activity = relationship("Activity", back_populates="photos")
    uploader = relationship("User", back_populates="uploaded_photos", foreign_keys=[uploaded_by])
    daycare = relationship("Daycare", back_populates="photos")


class Notification(Base):
    """Notification model"""
    __tablename__ = 'notifications'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, default={})
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime)
    sent_via = Column(JSON, default=[])  # ['email', 'sms', 'push']
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="notifications")


class Subscription(Base):
    """Subscription model"""
    __tablename__ = 'subscriptions'

    id = Column(String, primary_key=True, default=generate_uuid)
    daycare_id = Column(String, ForeignKey('daycares.id'), nullable=False, unique=True)
    plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE)

    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    stripe_price_id = Column(String)

    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)

    # Usage tracking
    photos_used_this_month = Column(Integer, default=0)
    ai_queries_used_today = Column(Integer, default=0)
    voice_minutes_used_this_month = Column(Integer, default=0)
    last_usage_reset = Column(DateTime, default=datetime.utcnow)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    daycare = relationship("Daycare", back_populates="subscription")


class ChatHistory(Base):
    """AI Chat history"""
    __tablename__ = 'chat_history'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    daycare_id = Column(String, ForeignKey('daycares.id'), nullable=False)
    messages = Column(JSON, default=[])  # Array of {role, content, timestamp}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VoiceCall(Base):
    """Voice call history"""
    __tablename__ = 'voice_calls'

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    daycare_id = Column(String, ForeignKey('daycares.id'), nullable=False)
    twilio_call_sid = Column(String)
    duration_seconds = Column(Integer, default=0)
    transcript = Column(Text)
    recording_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
