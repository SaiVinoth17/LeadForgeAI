import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def get_session():
    """Returns a requests Session with robust retry and backoff configured."""
    session = requests.Session()
    
    # Retry strategy: 3 total retries, backoff factor 0.5 (0.5s, 1s, 2s), retry on common transient errors
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    # Default User-Agent to avoid being blocked by simple scrapers
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 LeadForgeAI/2.0"
    })
    
    return session

network_session = get_session()
