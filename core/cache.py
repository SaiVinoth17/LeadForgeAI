import json
import time
from core.config import DATA_DIR
from core.logger import logger

CACHE_FILE = DATA_DIR / "cache.json"
CACHE_TTL = 86400  # 24 hours in seconds

import threading

class CacheManager:
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self._load()
        
    def _load(self):
        with self._lock:
            if CACHE_FILE.exists():
                try:
                    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                        self._cache = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load cache: {e}")
                    self._cache = {}
                
    def _save(self):
        with self._lock:
            try:
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self._cache, f)
            except Exception as e:
                logger.error(f"Failed to save cache: {e}")
            
    def get(self, key: str):
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() - entry.get('timestamp', 0) < CACHE_TTL:
                    return entry.get('data')
                else:
                    del self._cache[key]
                    try:
                        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                            json.dump(self._cache, f)
                    except Exception as e:
                        logger.error(f"Failed to save cache: {e}")
            return None
        
    def set(self, key: str, data):
        with self._lock:
            self._cache[key] = {
                'timestamp': time.time(),
                'data': data
            }
            try:
                with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self._cache, f)
            except Exception as e:
                logger.error(f"Failed to save cache: {e}")

cache_manager = CacheManager()
