import urllib.parse
from bs4 import BeautifulSoup
from core.logger import logger
from core.cache import cache_manager
from core.network import network_session

class BaseProvider:
    def search_leads(self, query: str, location: str, radius: int = 5000, max_results: int = 50):
        raise NotImplementedError

class GoogleProvider(BaseProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        
    def search_leads(self, query: str, location: str, radius: int = 5000, max_results: int = 20):
        # Implementation from google_places.py...
        results = []
        try:
            params = {"query": f"{query} in {location}", "key": self.api_key}
            response = network_session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            for item in data.get("results", [])[:max_results]:
                results.append({
                    "business_name": item.get("name"),
                    "address": item.get("formatted_address"),
                    "latitude": item.get("geometry", {}).get("location", {}).get("lat"),
                    "longitude": item.get("geometry", {}).get("location", {}).get("lng"),
                    "provider": "Google Places",
                    # Skipping details fetch here to save space since we deprecate this
                })
        except Exception as e:
            logger.error(f"GoogleProvider search error: {e}")
        return results

class OSMProvider(BaseProvider):
    TAG_MAPPINGS = {
        "hotel": "tourism=hotel",
        "restaurant": "amenity=restaurant",
        "cafe": "amenity=cafe",
        "hospital": "amenity=hospital",
        "dentist": "amenity=dentist",
        "school": "amenity=school",
        "salon": "shop=hairdresser",
        "gym": "leisure=fitness_centre",
        "pharmacy": "amenity=pharmacy",
        "bank": "amenity=bank",
        "atm": "amenity=atm",
        "electrician": "craft=electrician",
        "plumber": "craft=plumber",
        "lawyer": "office=lawyer",
        "company": "office=company",
        "office": "office=*",
        "store": "shop=*",
        "resort": "tourism=hotel",
        "travel agency": "office=travel_agent"
    }
    
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        
    def _geocode(self, location: str):
        cache_key = f"nominatim_{location}"
        cached = cache_manager.get(cache_key)
        if cached: return cached
        
        try:
            params = {"q": location, "format": "json", "limit": 1}
            logger.info(f"Geocoding {location} via Nominatim...")
            resp = network_session.get(self.nominatim_url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data:
                coords = (float(data[0]["lat"]), float(data[0]["lon"]))
                cache_manager.set(cache_key, coords)
                return coords
        except Exception as e:
            logger.error(f"Nominatim Error: {e}")
        return None

    def search_leads(self, query: str, location: str, radius: int = 5000, max_results: int = 50):
        coords = self._geocode(location)
        if not coords:
            logger.error("Could not geocode location.")
            return []
            
        lat, lon = coords
        tag_query = self.TAG_MAPPINGS.get(query.lower(), "name~'.*'")
        
        cache_key = f"overpass_{lat}_{lon}_{radius}_{tag_query}"
        cached = cache_manager.get(cache_key)
        if cached:
            return self._parse_overpass(cached, max_results)
            
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node[{tag_query}](around:{radius},{lat},{lon});
          way[{tag_query}](around:{radius},{lat},{lon});
          relation[{tag_query}](around:{radius},{lat},{lon});
        );
        out center;
        """
        
        endpoints = [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://lz4.overpass-api.de/api/interpreter",
            "https://z.overpass-api.de/api/interpreter"
        ]
        
        delay = 1
        import time
        for endpoint in endpoints:
            try:
                logger.info(f"Querying Overpass API for {tag_query} around {lat},{lon} using {endpoint}...")
                headers = {"User-Agent": "LeadForgeAI/2.0 (contact@example.com)"}
                resp = network_session.post(endpoint, data={"data": overpass_query}, headers=headers, timeout=20)
                
                if resp.status_code == 200:
                    data = resp.json()
                    logger.info(f"Overpass query succeeded on endpoint: {endpoint}")
                    cache_manager.set(cache_key, data)
                    return self._parse_overpass(data, max_results)
                    
                if resp.status_code in [429, 500, 502, 503, 504]:
                    logger.warning(f"Endpoint {endpoint} returned {resp.status_code}. Retrying next endpoint...")
                    time.sleep(delay)
                    delay *= 2
                    continue
                    
                resp.raise_for_status()
                
            except Exception as e:
                logger.warning(f"Endpoint {endpoint} failed with error: {e}")
                time.sleep(delay)
                delay *= 2
                continue
                
        raise Exception("ALL_SERVERS_UNAVAILABLE")

    def _parse_overpass(self, data, max_results):
        results = []
        elements = data.get("elements", [])
        for el in elements[:max_results]:
            tags = el.get("tags", {})
            name = tags.get("name")
            if not name:
                continue
                
            osm_id = str(el.get("id"))
            
            # Determine lat/lon based on element type
            if el["type"] == "node":
                lat, lon = el.get("lat"), el.get("lon")
            else:
                center = el.get("center", {})
                lat, lon = center.get("lat"), center.get("lon")
                
            website = tags.get("website", tags.get("contact:website", ""))
            if not website:
                website = self._discover_website(name, tags.get("addr:city", ""))
                
            phone = tags.get("phone", tags.get("contact:phone", ""))
            email = tags.get("email", tags.get("contact:email", ""))
            
            street = tags.get("addr:street", "")
            housenumber = tags.get("addr:housenumber", "")
            address = f"{housenumber} {street}".strip()
            city = tags.get("addr:city", "")
            
            results.append({
                "osm_id": osm_id,
                "business_name": name,
                "address": address,
                "city": city,
                "phone": phone,
                "email": email,
                "website": website,
                "latitude": lat,
                "longitude": lon,
                "provider": "OpenStreetMap",
                "category": tags.get("amenity", tags.get("shop", tags.get("office", "")))
            })
            
        return results

    def _discover_website(self, name, city):
        search_query = f"{name} {city} official website".strip()
        cache_key = f"discover_web_{search_query}"
        cached = cache_manager.get(cache_key)
        if cached is not None:
            return cached # Can be empty string
            
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            logger.info(f"Discovering website for {search_query} via DuckDuckGo...")
            # rate limiting logic handled by session retries/backoffs usually, but keep a tiny sleep just in case
            import time; time.sleep(1) 
            resp = network_session.post(url, data={"q": search_query}, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                for a in soup.find_all('a', class_='result__url'):
                    href = a.get('href')
                    if href and 'duckduckgo.com' not in href:
                        website = href.strip()
                        if website.startswith('//'):
                            website = 'https:' + website
                        # Decode DDG redirect
                        parsed = urllib.parse.urlparse(website)
                        qs = urllib.parse.parse_qs(parsed.query)
                        if 'uddg' in qs:
                            website = qs['uddg'][0]
                        cache_manager.set(cache_key, website)
                        return website
        except Exception as e:
            logger.error(f"Website discovery error for {search_query}: {e}")
            
        cache_manager.set(cache_key, "")
        return ""
