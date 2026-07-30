from database.db_manager import db_manager
from models.lead import Lead, Setting
from core.logger import logger
from core.events import event_bus, Events

import re

def normalize_string(s: str) -> str:
    if not s:
        return ""
    return re.sub(r'[^a-z0-9]', '', str(s).lower())

def is_duplicate(session, lead_data: dict) -> bool:
    from sqlalchemy import or_
    
    raw_osm_id = lead_data.get('osm_id', '')
    osm_id = str(raw_osm_id) if raw_osm_id is not None else ''
    website = lead_data.get('website', '')
    phone = lead_data.get('phone', '')
    email = lead_data.get('email', '')
    b_name = lead_data.get('business_name', '')
    city = lead_data.get('city', '')
    
    filters = []
    if osm_id:
        filters.append(Lead.osm_id == osm_id)
    if website:
        filters.append(Lead.website.ilike(website))
    if phone:
        filters.append(Lead.phone == phone)
    if email:
        filters.append(Lead.email.ilike(email))
    if b_name and city:
        filters.append((Lead.business_name.ilike(b_name)) & (Lead.city.ilike(city)))
        
    if not filters:
        return False
        
    # Query only candidates matching any of these criteria
    candidates = session.query(Lead).filter(or_(*filters)).all()
    
    norm_osm_id = osm_id
    norm_website = normalize_string(website)
    norm_phone = normalize_string(phone)
    norm_email = normalize_string(email)
    norm_b_name = normalize_string(b_name)
    norm_city = normalize_string(city)
    
    for l in candidates:
        if norm_osm_id and str(l.osm_id) == norm_osm_id: return True
        if norm_website and normalize_string(l.website) == norm_website: return True
        if norm_phone and normalize_string(l.phone) == norm_phone: return True
        if norm_b_name and norm_city and normalize_string(l.business_name) == norm_b_name and normalize_string(l.city) == norm_city: return True
        if norm_email and normalize_string(l.email) == norm_email: return True
        
    return False

def add_lead(lead_data: dict) -> Lead:
    session = db_manager.get_session()
    try:
        if is_duplicate(session, lead_data):
            logger.info(f"Duplicate lead skipped: {lead_data.get('business_name')}")
            return None
            
        new_lead = Lead(**lead_data)
        session.add(new_lead)
        session.commit()
        session.refresh(new_lead)
        event_bus.emit(Events.LEAD_ADDED, new_lead)
        return new_lead
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding lead: {e}")
        return None
    finally:
        session.close()

def get_all_leads():
    session = db_manager.get_session()
    try:
        return session.query(Lead).order_by(Lead.created_date.desc()).all()
    except Exception as e:
        logger.error(f"Error getting leads: {e}")
        return []
    finally:
        session.close()

def update_lead(lead_id: int, update_data: dict):
    session = db_manager.get_session()
    try:
        lead = session.query(Lead).filter(Lead.id == lead_id).first()
        if lead:
            for key, value in update_data.items():
                setattr(lead, key, value)
            session.commit()
            session.refresh(lead)
            event_bus.emit(Events.LEAD_UPDATED, lead)
            return lead
        return None
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating lead {lead_id}: {e}")
        return None
    finally:
        session.close()

def delete_lead(lead_id: int):
    session = db_manager.get_session()
    try:
        lead = session.query(Lead).filter(Lead.id == lead_id).first()
        if lead:
            session.delete(lead)
            session.commit()
            event_bus.emit(Events.LEAD_DELETED, lead_id)
            return True
        return False
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting lead {lead_id}: {e}")
        return False
    finally:
        session.close()

def get_setting(key: str, default=None):
    session = db_manager.get_session()
    try:
        setting = session.query(Setting).filter(Setting.key == key).first()
        if setting:
            return setting.value
        return default
    except Exception as e:
        logger.error(f"Error getting setting {key}: {e}")
        return default
    finally:
        session.close()

def set_setting(key: str, value: str):
    session = db_manager.get_session()
    try:
        setting = session.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = str(value)
        else:
            setting = Setting(key=key, value=str(value))
            session.add(setting)
        session.commit()
        event_bus.emit(Events.SETTINGS_CHANGED, key, value)
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error setting {key}: {e}")
        return False
    finally:
        session.close()
