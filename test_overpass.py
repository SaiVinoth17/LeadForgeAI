import logging
import json
import requests
logging.basicConfig(level=logging.DEBUG)

from core.network import network_session
from services.providers import OSMProvider
import core.cache

provider = OSMProvider()

def my_search_leads(query, location, radius=5000):
    coords = provider._geocode(location)
    print('\n1. Nominatim Coords:', coords)
    
    lat, lon = coords
    tag_query = provider.TAG_MAPPINGS.get(query.lower(), "name~'.*'")
    
    overpass_query = f"""
    [out:json][timeout:25];
    (
      node[{tag_query}](around:{radius},{lat},{lon});
      way[{tag_query}](around:{radius},{lat},{lon});
      relation[{tag_query}](around:{radius},{lat},{lon});
    );
    out center;
    """
    print('\n2. Overpass Query:', overpass_query.strip())
    
    headers = {
        'User-Agent': 'LeadForgeAI-Test/1.0 (contact@example.com)'
    }
    try:
        resp = requests.post(provider.overpass_url, data={'data': overpass_query}, headers=headers, timeout=30)
        print('\n3. HTTP Status:', resp.status_code)
        
        if resp.status_code != 200:
            print('Raw text:', resp.text[:200])
            return
            
        data = resp.json()
        print('\n4. Raw Response Keys:', list(data.keys()))
        if 'remark' in data:
            print('   Remark:', data['remark'])
        
        elements = data.get('elements', [])
        print('\n5. Parsed Element Count:', len(elements))
    except Exception as e:
        print('\nFailed to parse JSON:', e)
        if 'resp' in locals():
            print('Raw text:', resp.text[:200])

my_search_leads('Hotel', 'Ooty')
