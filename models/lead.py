"""
Lead Database Model.
Defines the schema for stored leads and application settings.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Lead(Base):
    """
    Lead model representing a business prospect in the CRM.
    """
    __tablename__ = 'leads'
    
    # Core Fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    business_name = Column(String(255), nullable=False)
    category = Column(String(255), index=True)
    phone = Column(String(50), index=True)
    website = Column(String(255), index=True)
    email = Column(String(255))
    google_maps_url = Column(String(500))
    address = Column(String(255))
    city = Column(String(100), index=True)
    state = Column(String(100))
    country = Column(String(100))
    rating = Column(Float)
    reviews = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # CRM Fields
    status = Column(String(50), default="Discovery", index=True) # Discovery, Qualified, Proposal, Meeting, Negotiation, Won, Lost
    priority = Column(String(50), default="Cold", index=True) # High Opportunity, Medium, Low
    notes = Column(Text)
    proposal = Column(Text)
    email_draft = Column(Text)
    whatsapp_draft = Column(Text)
    call_script = Column(Text)
    meeting_points = Column(Text)
    meeting_date = Column(DateTime, nullable=True)
    followup_date = Column(DateTime, nullable=True)
    estimated_value = Column(Float, default=0.0)
    screenshot_path = Column(String(500))
    last_contacted = Column(DateTime, nullable=True)
    
    # Provider & Migration Fields
    provider = Column(String(50), default="OpenStreetMap")
    osm_id = Column(String(100), index=True)
    lead_score = Column(Integer, index=True, default=0) # Legacy
    opportunity_score = Column(Integer, index=True, default=0)
    confidence_score = Column(Integer, default=0)
    confidence_reasons = Column(Text)
    analysis_date = Column(DateTime, nullable=True)
    
    # Website Analyzer specific fields
    website_status = Column(String(50))
    website_type = Column(String(50)) # None, Facebook, Instagram, WhatsApp, Professional
    has_professional_email = Column(String(10))
    has_online_booking = Column(String(10))
    has_logo = Column(String(10))
    
    has_ssl = Column(String(10))
    is_mobile_responsive = Column(String(10))
    detected_framework = Column(String(100)) # Legacy, will keep to prevent breaking old DBs without complex migrations
    detected_frameworks = Column(Text) # JSON string of all frameworks
    analytics_tags = Column(Text) # JSON string of analytics
    has_contact_page = Column(String(10))
    has_whatsapp = Column(String(10))
    social_links = Column(Text) # JSON string
    ai_summary = Column(Text)
    
    def __repr__(self) -> str:
        return f"<Lead(name='{self.business_name}', status='{self.status}', priority='{self.priority}')>"

class Setting(Base):
    """
    Key-Value store for application settings.
    """
    __tablename__ = 'settings'
    
    key = Column(String(100), primary_key=True)
    value = Column(Text)
