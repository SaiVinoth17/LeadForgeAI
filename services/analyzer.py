import requests
from bs4 import BeautifulSoup
import re
import ssl
import socket
from urllib.parse import urlparse, urljoin
import time
from core.logger import logger
from core.network import network_session

def fast_analyze_lead(lead_data: dict) -> dict:
    """Performs a quick, non-network analysis on raw lead data to determine opportunity metrics."""
    website = lead_data.get("website", "").lower()
    email = lead_data.get("email", "").lower()
    
    website_type = "None"
    if website:
        if "facebook.com" in website:
            website_type = "Facebook"
        elif "instagram.com" in website:
            website_type = "Instagram"
        elif "wa.me" in website or "api.whatsapp.com" in website:
            website_type = "WhatsApp"
        else:
            website_type = "Professional"
            
    has_professional_email = "No"
    if email:
        free_providers = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com", "icloud.com", "me.com", "msn.com"]
        domain = email.split('@')[-1] if '@' in email else ""
        if domain and domain not in free_providers:
            has_professional_email = "Yes"
            
    # Calculate base opportunity score
    opp_score = 0
    if website_type == "None": opp_score += 50
    elif website_type == "Facebook": opp_score += 20
    elif website_type == "Instagram": opp_score += 15
    elif website_type == "WhatsApp": opp_score += 15
    elif website_type == "Professional": opp_score -= 50
    
    if has_professional_email == "No": opp_score += 10
    
    # Rating and Reviews
    rating = lead_data.get("rating")
    try:
        rating = float(rating) if rating else 0
        if rating > 4.5: opp_score += 10
    except: pass
    
    reviews = lead_data.get("reviews")
    try:
        reviews = int(reviews) if reviews else 0
        if reviews > 50: opp_score += 10
    except: pass
    
    return {
        "website_type": website_type,
        "has_professional_email": has_professional_email,
        "opportunity_score": opp_score
    }

class WebsiteAnalyzer:
    def __init__(self, lead_model_or_url):
        if isinstance(lead_model_or_url, str):
            self.lead = None
            self.url = lead_model_or_url
        else:
            self.lead = lead_model_or_url
            self.url = self.lead.website if self.lead and hasattr(self.lead, "website") else ""
        
        if self.url and not self.url.startswith(('http://', 'https://')):
            self.url = 'https://' + self.url
            
        self.domain = urlparse(self.url).netloc if self.url else ""
        self.html_content = ""
        self.soup = None
        self.response = None
        self.response_time = 0.0
        
        # Initialize results with fast metrics
        web_val = self.lead.website if self.lead else self.url
        email_val = self.lead.email if self.lead else ""
        fast_res = fast_analyze_lead({"website": web_val, "email": email_val})
        self.results = {
            "has_ssl": "No",
            "is_mobile_responsive": "No",
            "detected_frameworks": [],
            "analytics_tags": [],
            "seo_title": "No",
            "seo_description": "No",
            "seo_open_graph": "No",
            "seo_twitter_cards": "No",
            "seo_json_ld": "No",
            "seo_h1_h2": "No",
            "seo_alt_tags": "No",
            "has_robots_txt": "No",
            "has_sitemap": "No",
            "has_favicon": "No",
            "canonical_tag": "No",
            "security_headers": "No",
            "mixed_content": "No",
            "compression": "No",
            "cache_headers": "No",
            "redirects": 0,
            "response_time_ms": 0,
            "broken_images": 0,
            "has_contact_page": "No",
            "has_whatsapp": "No",
            "has_online_booking": "No",
            "has_logo": "No",
            "social_links": [],
            "emails": [],
            "website_type": fast_res["website_type"],
            "has_professional_email": fast_res["has_professional_email"],
            "opportunity_score": fast_res["opportunity_score"],
            "lead_priority": "Low",
            "ai_summary": "",
            "estimated_value": 0.0
        }

    def fetch(self):
        if not self.url or self.results["website_type"] in ["Facebook", "Instagram", "WhatsApp"]:
            # Do not fetch if no website or social profile
            return False
            
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 LeadForgeAI/2.0'
            }
            start_time = time.time()
            self.response = network_session.get(self.url, headers=headers, timeout=10, allow_redirects=True)
            self.response_time = time.time() - start_time
            self.results["response_time_ms"] = int(self.response_time * 1000)
            self.results["redirects"] = len(self.response.history)
            
            self.html_content = self.response.text
            self.soup = BeautifulSoup(self.html_content, 'html.parser')
            
            # Security Headers
            if 'Strict-Transport-Security' in self.response.headers or 'Content-Security-Policy' in self.response.headers:
                self.results["security_headers"] = "Yes"
                
            # Compression
            if 'Content-Encoding' in self.response.headers and self.response.headers['Content-Encoding'] in ['gzip', 'br', 'deflate']:
                self.results["compression"] = "Yes"
                
            # Cache Headers
            if 'Cache-Control' in self.response.headers:
                self.results["cache_headers"] = "Yes"
                
            return True
        except Exception as e:
            logger.error(f"Failed to fetch {self.url}: {e}")
            return False

    def check_ssl(self):
        if self.url.startswith('https'):
            try:
                context = ssl.create_default_context()
                with socket.create_connection((self.domain, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                        if ssock.version():
                            self.results["has_ssl"] = "Yes"
            except Exception as e:
                logger.error(f"SSL Check failed for {self.domain}: {e}")

    def analyze_seo_and_responsive(self):
        if not self.soup: return
        
        # Responsive
        meta_viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        if meta_viewport and 'width=device-width' in meta_viewport.get('content', '').lower():
            self.results["is_mobile_responsive"] = "Yes"
            
        # Standard SEO
        if self.soup.title and self.soup.title.string:
            self.results["seo_title"] = "Yes"
        if self.soup.find('meta', attrs={'name': 'description'}):
            self.results["seo_description"] = "Yes"
            
        # Social SEO
        if self.soup.find('meta', attrs={'property': re.compile(r'^og:')}):
            self.results["seo_open_graph"] = "Yes"
        if self.soup.find('meta', attrs={'name': re.compile(r'^twitter:')}):
            self.results["seo_twitter_cards"] = "Yes"
            
        # JSON-LD
        if self.soup.find('script', type='application/ld+json'):
            self.results["seo_json_ld"] = "Yes"
            
        # Favicon
        if self.soup.find('link', rel=re.compile(r'icon')):
            self.results["has_favicon"] = "Yes"
            
        # Canonical
        if self.soup.find('link', rel='canonical'):
            self.results["canonical_tag"] = "Yes"
            
        # Hierarchy
        h1 = self.soup.find_all('h1')
        h2 = self.soup.find_all('h2')
        if len(h1) == 1 and len(h2) > 0:
            self.results["seo_h1_h2"] = "Yes"
            
        # Images Alt & Mixed Content
        images = self.soup.find_all('img')
        missing_alt = 0
        has_logo = False
        for img in images:
            alt = img.get('alt', '').lower()
            if not alt:
                missing_alt += 1
            if 'logo' in alt or 'logo' in img.get('class', []) or 'logo' in img.get('id', ''):
                has_logo = True
                
            src = img.get('src', '')
            if src.startswith('http://') and self.url.startswith('https://'):
                self.results["mixed_content"] = "Yes"
                
        if has_logo:
            self.results["has_logo"] = "Yes"
            
        if images and missing_alt == 0:
            self.results["seo_alt_tags"] = "Yes"

    def check_endpoints(self):
        # Quick HEAD checks for robots and sitemap
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            r1 = requests.head(urljoin(self.url, '/robots.txt'), headers=headers, timeout=5)
            if r1.status_code == 200: self.results["has_robots_txt"] = "Yes"
            
            r2 = requests.head(urljoin(self.url, '/sitemap.xml'), headers=headers, timeout=5)
            if r2.status_code == 200: self.results["has_sitemap"] = "Yes"
        except:
            pass

    def detect_technologies(self):
        if not self.soup: return
        frameworks = []
        analytics = []
        content_lower = self.html_content.lower()
        
        # Extended Frameworks & CMS
        if self.soup.find(attrs={"id": "___gatsby"}): frameworks.append("Gatsby")
        if self.soup.find(attrs={"id": "__next"}): frameworks.append("Next.js")
        if self.soup.find(attrs={"id": "root"}) or 'react' in content_lower: frameworks.append("React")
        if 'vue' in content_lower or self.soup.find(attrs={"data-v-app": True}): frameworks.append("Vue")
        if 'ng-version' in content_lower: frameworks.append("Angular")
        if 'svelte' in content_lower or 'data-sveltekit' in content_lower: frameworks.append("Svelte")
        if 'astro-' in content_lower: frameworks.append("Astro")
        if '__nuxt' in content_lower: frameworks.append("Nuxt")
        if 'wp-content' in content_lower: frameworks.append("WordPress")
        if 'shopify' in content_lower: frameworks.append("Shopify")
        if 'magento' in content_lower: frameworks.append("Magento")
        if 'wix.com' in content_lower: frameworks.append("Wix")
        if 'squarespace' in content_lower: frameworks.append("Squarespace")
        if 'drupal' in content_lower: frameworks.append("Drupal")
        if 'joomla' in content_lower: frameworks.append("Joomla")
        if 'bootstrap' in content_lower: frameworks.append("Bootstrap")
        if 'tailwind' in content_lower: frameworks.append("Tailwind")
        
        # Analytics & Trackers
        if 'googletagmanager.com' in content_lower: analytics.append("Google Tag Manager")
        if 'google-analytics.com' in content_lower: analytics.append("Google Analytics")
        if 'fbq(' in content_lower or 'connect.facebook.net' in content_lower: analytics.append("Meta Pixel")
        if 'hotjar' in content_lower: analytics.append("Hotjar")
        if 'clarity.ms' in content_lower: analytics.append("Microsoft Clarity")
        if 'recaptcha' in content_lower: analytics.append("reCAPTCHA")
        if '__cf_email__' in content_lower or 'cloudflare' in self.response.headers.get('server', '').lower(): analytics.append("Cloudflare")
        
        # Booking engines
        booking_keywords = ['calendly.com', 'fresha.com', 'setmore.com', 'acuityscheduling.com', 'mindbodyonline.com', 'vagaro.com', 'simplybook.me', 'booksy.com', 'opentable.com', 'resy.com']
        has_booking = False
        for kw in booking_keywords:
            if kw in content_lower:
                has_booking = True
                break
        
        if not has_booking:
            links = self.soup.find_all('a', href=True)
            for link in links:
                text = link.get_text().lower()
                href = link['href'].lower()
                if 'book now' in text or 'book appointment' in text or 'book online' in text:
                    has_booking = True
                    break
                    
        if has_booking:
            self.results["has_online_booking"] = "Yes"
        
        self.results["detected_frameworks"] = list(set(frameworks))
        self.results["analytics_tags"] = list(set(analytics))

    def find_contact_info(self):
        if not self.soup: return
        
        if 'wa.me' in self.html_content or 'api.whatsapp.com' in self.html_content:
            self.results["has_whatsapp"] = "Yes"
            
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, self.html_content)
        self.results["emails"] = list(set([e for e in emails if not e.endswith(('png','jpg','jpeg','gif','webp','svg'))]))
        
        links = self.soup.find_all('a', href=True)
        social_domains = ['facebook.com', 'instagram.com', 'twitter.com', 'linkedin.com', 'youtube.com']
        
        for link in links:
            href = link['href'].lower()
            if 'contact' in href:
                self.results["has_contact_page"] = "Yes"
            for social in social_domains:
                if social in href:
                    self.results["social_links"].append(link['href'])
                
        self.results["social_links"] = list(set(self.results["social_links"]))

    def generate_score_and_priority(self):
        score = self.results["opportunity_score"]
        reasons = []
        
        # Build Reasons list in the format required: "✓ [Reason]"
        if self.results["website_type"] == "None":
            reasons.append("✓ No Website")
        elif self.results["website_type"] == "Facebook":
            reasons.append("✓ Facebook Only")
        elif self.results["website_type"] == "Instagram":
            reasons.append("✓ Instagram Only")
        elif self.results["website_type"] == "WhatsApp":
            reasons.append("✓ WhatsApp Only")
            
        if self.results["has_professional_email"] == "No":
            reasons.append("✓ Uses Free Email (Gmail/Yahoo)")
            
        rating = self.lead.rating if (self.lead and hasattr(self.lead, "rating")) else 0
        rating = rating or 0
        if rating > 4.5:
            reasons.append(f"✓ {rating} Rating")
            
        reviews = self.lead.reviews if (self.lead and hasattr(self.lead, "reviews")) else 0
        reviews = reviews or 0
        if reviews > 50:
            reasons.append(f"✓ {reviews} Reviews")
            
        phone = self.lead.phone if (self.lead and hasattr(self.lead, "phone")) else ""
        if phone:
            reasons.append("✓ Phone Available")
            
        if self.results["has_whatsapp"] == "Yes" or self.results["website_type"] == "WhatsApp":
            if "✓ WhatsApp Available" not in reasons and "✓ WhatsApp Only" not in reasons:
                reasons.append("✓ WhatsApp Available")
            
        if self.results["website_type"] == "Professional":
            # Penalties for having a modern/professional site
            if self.results["detected_frameworks"]:
                score -= 30  # Modern Website penalty
                reasons.append("❌ Uses Modern Framework")
            
            # Major opportunity points for critical failures:
            if self.results["has_ssl"] == "No":
                score += 20
                reasons.append("✓ No SSL Security")
            if self.results["is_mobile_responsive"] == "No":
                score += 25
                reasons.append("✓ Not Mobile Responsive")
            if self.results["response_time_ms"] > 2500:
                score += 15
                reasons.append("✓ Slow Page Load Speed")
                
            if self.results["has_online_booking"] == "No": 
                score += 10
                reasons.append("✓ No Online Booking")
            if self.results["has_logo"] == "No": 
                score += 10
                reasons.append("✓ Poor Branding (No Logo)")
                
        score = max(0, min(100, score)) # Clamp between 0 and 100
        self.results["opportunity_score"] = score
        
        if score >= 75:
            self.results["lead_priority"] = "High Opportunity"
            badge = "🔥 Excellent Opportunity"
        elif score >= 50:
            self.results["lead_priority"] = "Medium"
            badge = "🟠 High"
        elif score >= 25:
            self.results["lead_priority"] = "Low"
            badge = "🟡 Medium"
        else:
            self.results["lead_priority"] = "Low"
            badge = "⚪ Low"
            
        # --- Confidence Score Calculation ---
        # Starts at 50, goes up based on verified data points
        conf = 50
        conf_reasons = []
        if self.results["website_type"] != "None": 
            conf += 10; conf_reasons.append("Website analyzed")
        phone = self.lead.phone if (self.lead and hasattr(self.lead, "phone")) else ""
        if phone: 
            conf += 15; conf_reasons.append("Phone verified")
        if rating > 0: 
            conf += 10; conf_reasons.append(f"Rating {rating}")
        if reviews > 0: 
            conf += 10; conf_reasons.append(f"Reviews {reviews}")
        email = self.lead.email if (self.lead and hasattr(self.lead, "email")) else ""
        if email: 
            conf += 5; conf_reasons.append("Email detected")
            
        conf = min(99, conf) # Max 99% confident
        self.results["confidence_score"] = conf
        self.results["confidence_reasons"] = ", ".join(conf_reasons)
        
        summary_lines = [badge, f"Confidence: {conf}%", "", "Reasons"] + reasons
        self.results["ai_summary"] = "\n".join(summary_lines)
        
        # Estimate Value
        cat = str(self.lead.category).lower() if (self.lead and hasattr(self.lead, "category") and self.lead.category) else ""
        if self.results["website_type"] in ["None", "Facebook", "Instagram", "WhatsApp"]:
            if "hotel" in cat or "resort" in cat or "dentist" in cat or "lawyer" in cat:
                self.results["estimated_value"] = 65000.0 # High value industry needing booking/trust
            elif "restaurant" in cat or "cafe" in cat:
                self.results["estimated_value"] = 45000.0
            else:
                self.results["estimated_value"] = 35000.0 # Basic landing page/business site
        else:
            # They have a site, so pitching optimization/rebuild
            self.results["estimated_value"] = 25000.0

    def run_analysis(self):
        if self.results["website_type"] == "Professional":
            if self.fetch():
                self.check_ssl()
                self.analyze_seo_and_responsive()
                self.check_endpoints()
                self.detect_technologies()
                self.find_contact_info()
        
        self.generate_score_and_priority()
        return self.results
