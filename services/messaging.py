import urllib.parse
import re

class MessagingService:
    @staticmethod
    def generate_whatsapp_link(phone: str, message: str = "") -> str:
        if not phone:
            return ""
        
        # Clean phone number (remove everything except digits and '+')
        clean_phone = re.sub(r'[^\d+]', '', phone)
        if not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone # Assume international format needed, but might be flawed.
            
        base_url = f"https://wa.me/{clean_phone.replace('+', '')}"
        
        if message:
            encoded_msg = urllib.parse.quote(message)
            return f"{base_url}?text={encoded_msg}"
            
        return base_url

    @staticmethod
    def generate_email_draft(email: str, subject: str, body: str) -> str:
        if not email:
            return ""
            
        encoded_subject = urllib.parse.quote(subject)
        encoded_body = urllib.parse.quote(body)
        
        return f"mailto:{email}?subject={encoded_subject}&body={encoded_body}"
