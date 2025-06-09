from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Date, Time, ForeignKey, Text, Enum, ARRAY
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date, time
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Pydantic Schemas for API responses
class ChatMessageSchema(BaseModel):
    id: int
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

class ChatConversationSchema(BaseModel):
    id: uuid.UUID
    user_id: int
    created_at: datetime
    last_updated: datetime
    messages: List[ChatMessageSchema] = []

    class Config:
        from_attributes = True

Base = declarative_base()

# SQLAlchemy ORM Models
class UserInDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    type = Column(String, nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roadmaps = relationship("RoadmapInDB", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)

class RoadmapInDB(Base):
    __tablename__ = "roadmaps"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    budget_total = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("UserInDB", back_populates="roadmaps")
    days = relationship("RoadmapDayInDB", back_populates="roadmap", cascade="all, delete-orphan")
    tickets = relationship("Ticket", back_populates="roadmap", cascade="all, delete-orphan")
    accommodations = relationship("AccommodationInDB", back_populates="roadmap", cascade="all, delete-orphan")
    places = relationship("Place", back_populates="roadmap", cascade="all, delete-orphan")
    food_places = relationship("FoodPlaceInDB", back_populates="roadmap", cascade="all, delete-orphan")

class RoadmapDayInDB(Base):
    __tablename__ = "roadmap_days"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    day_index = Column(Integer)
    date = Column(Date)
    summary = Column(Text)
    
    # Relationships
    roadmap = relationship("RoadmapInDB", back_populates="days")
    tasks = relationship("RoadmapTaskInDB", back_populates="day", cascade="all, delete-orphan")

class RoadmapTaskInDB(Base):
    __tablename__ = "roadmap_tasks"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_day_id = Column(Integer, ForeignKey("roadmap_days.id"))
    type = Column(String)
    title = Column(String)
    description = Column(Text)
    start_time = Column(Time)
    end_time = Column(Time)
    linked_id = Column(Integer)
    link_type = Column(String)
    
    # Relationships
    day = relationship("RoadmapDayInDB", back_populates="tasks")

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    type = Column(String)
    from_ = Column("from", String)
    to = Column(String)
    departure = Column(DateTime)
    arrival = Column(DateTime)
    price = Column(Integer)
    provider_url = Column(String)
    
    # Relationships
    roadmap = relationship("RoadmapInDB", back_populates="tickets")

class AccommodationInDB(Base):
    __tablename__ = "accommodations"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    name = Column(String)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    price_total = Column(Integer)
    location = Column(String)
    provider_url = Column(String)
    
    # Relationships
    roadmap = relationship("RoadmapInDB", back_populates="accommodations")

class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    name = Column(String)
    category = Column(String)
    location = Column(String)
    duration_min = Column(Integer)
    rating = Column(Float)
    url = Column(String)
    
    # Relationships
    roadmap = relationship("RoadmapInDB", back_populates="places")

class FoodPlaceInDB(Base):
    __tablename__ = "food_places"
    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"))
    name = Column(String)
    category = Column(String)
    location = Column(String)
    avg_price = Column(Integer)
    rating = Column(Float)
    url = Column(String)
    
    # Relationships
    roadmap = relationship("RoadmapInDB", back_populates="food_places")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_type = Column(ARRAY(String))
    interests = Column(ARRAY(String))
    daily_budget = Column(Integer)
    accommodation_type = Column(String)
    walking_or_guided = Column(String)
    
    # Relationships
    user = relationship("UserInDB", back_populates="preferences")
    
class Token(BaseModel):
    access_token: str
    type: str

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

    class Config:
        from_attributes = True

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("chat_conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("ChatConversation", back_populates="messages")

    class Config:
        from_attributes = True