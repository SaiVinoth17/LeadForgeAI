import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from core.config import DATA_DIR
from core.logger import logger
from database.crud import db_manager
from models.lead import Lead

SCREENSHOTS_DIR = DATA_DIR / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

CACHE_DURATION_DAYS = 7
CACHE_DURATION_SECONDS = CACHE_DURATION_DAYS * 86400

class ScreenshotEngine:
    def __init__(self):
        pass

    def _should_recapture(self, lead: Lead, force_refresh: bool = False) -> bool:
        if force_refresh:
            return True
            
        if not lead.screenshot_path:
            return True
            
        desktop_path = SCREENSHOTS_DIR / f"{lead.id}_desktop.png"
        if not desktop_path.exists():
            return True
            
        file_mtime = desktop_path.stat().st_mtime
        if time.time() - file_mtime > CACHE_DURATION_SECONDS:
            return True
            
        return False

    def capture(self, lead_id: int, force_refresh: bool = False):
        session = db_manager.get_session()
        try:
            lead = session.query(Lead).filter(Lead.id == lead_id).first()
            if not lead or not lead.website:
                return False

            website = lead.website
            if not website.startswith("http"):
                website = "https://" + website
                
            if not self._should_recapture(lead, force_refresh):
                logger.info(f"Using cached screenshot for Lead {lead.id}")
                return True

            logger.info(f"Capturing screenshots for Lead {lead.id} ({website})")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    # Desktop
                    context_desktop = browser.new_context(viewport={"width": 1280, "height": 720})
                    page_desktop = context_desktop.new_page()
                    try:
                        page_desktop.goto(website, timeout=30000, wait_until="networkidle")
                        desktop_path = SCREENSHOTS_DIR / f"{lead.id}_desktop.png"
                        page_desktop.screenshot(path=str(desktop_path), full_page=True)
                    except Exception as e:
                        logger.error(f"Desktop screenshot failed for {website}: {e}")
                    finally:
                        context_desktop.close()
                        
                    # Mobile
                    context_mobile = browser.new_context(
                        viewport={"width": 390, "height": 844},
                        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
                    )
                    page_mobile = context_mobile.new_page()
                    try:
                        page_mobile.goto(website, timeout=30000, wait_until="networkidle")
                        mobile_path = SCREENSHOTS_DIR / f"{lead.id}_mobile.png"
                        page_mobile.screenshot(path=str(mobile_path), full_page=True)
                    except Exception as e:
                        logger.error(f"Mobile screenshot failed for {website}: {e}")
                    finally:
                        context_mobile.close()
                finally:
                    browser.close()

            lead.screenshot_path = str(SCREENSHOTS_DIR / f"{lead.id}_desktop.png")
            session.commit()
            return True

        except Exception as e:
            logger.error(f"Screenshot Engine Error: {e}")
            session.rollback()
            return False
        finally:
            session.close()

screenshot_engine = ScreenshotEngine()
