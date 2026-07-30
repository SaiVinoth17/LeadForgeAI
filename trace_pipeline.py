import sys
import logging
from unittest.mock import patch
import customtkinter as ctk

from ui.pages.lead_generator import LeadGeneratorPage
from services.providers import OSMProvider
from database.crud import add_lead, is_duplicate
import database.crud
import core.network
import core.cache

# Disable noisy logging
logging.getLogger().setLevel(logging.CRITICAL)
core.cache.cache_manager.get = lambda x: None

class Tracer:
    def __init__(self):
        self.stage = 0
        
    def log(self, stage_name, input_data, output_data):
        print(f"\n{stage_name}")
        print("Input:")
        print(input_data)
        print("\n->\n")
        print("Output:")
        print(output_data)
        print("\n->\n")
        
        # Determine count from output_data if possible
        count = None
        if isinstance(output_data, str) and "businesses" in output_data:
            count = int(output_data.split()[0])
        elif isinstance(output_data, (int, str)) and str(output_data).isdigit():
            count = int(output_data)
            
        if count == 0:
            print(f"STOPPING EXECUTION: Count became zero at {stage_name}")
            sys.exit(0)

tracer = Tracer()
original_search_leads = OSMProvider.search_leads
original_post = core.network.network_session.post
original_get = core.network.network_session.get

def patched_post(*args, **kwargs):
    tracer.log("HTTP Request", args[0], "Sending POST")
    
    resp = original_post(*args, **kwargs)
    
    try:
        data = resp.json()
        ctype = type(data).__name__
        count = len(data.get('elements', [])) if isinstance(data, dict) else len(data)
    except:
        ctype = "Parse Failed"
        count = 0
        
    tracer.log("HTTP Response", f"Status: {resp.status_code}, Length: {len(resp.text)}", f"{count} businesses")
    return resp

def patched_get(*args, **kwargs):
    tracer.log("HTTP Request", args[0], "Sending GET")
    
    resp = original_get(*args, **kwargs)
    
    try:
        data = resp.json()
        ctype = type(data).__name__
        count = len(data)
    except:
        ctype = "Parse Failed"
        count = 0
        
    tracer.log("HTTP Response", f"Status: {resp.status_code}, Length: {len(resp.text)}", f"{count} businesses")
    return resp

core.network.network_session.post = patched_post
core.network.network_session.get = patched_get

def patched_search_leads(self, query, location, radius=5000, max_results=50):
    tracer.log("Search Button", f"{query}\n{location}", "Routing to OSMProvider")
    
    results = original_search_leads(self, query, location, radius, max_results)
    tracer.log("OSMProvider", "Querying provider", f"{len(results)} businesses")
    return results

OSMProvider.search_leads = patched_search_leads

def patched_add_lead(lead_data):
    # This simulates Duplicate Detection -> Database Import
    return database.crud.original_add_lead(lead_data)

if not hasattr(database.crud, 'original_add_lead'):
    database.crud.original_add_lead = database.crud.add_lead
database.crud.add_lead = patched_add_lead

def test():
    app = ctk.CTk()
    page = LeadGeneratorPage(app)
    
    # Run _run_search synchronously
    page.after = lambda ms, f: f()
    page.query_var.set("Hotel")
    page.location_var.set("Ooty")
    
    # We will track UI results
    original_add_result = page._add_result_row
    added_count = [0]
    def mock_add(*args):
        added_count[0] += 1
    page._add_result_row = mock_add
    
    page._run_search("Hotel", "Ooty")
    
    tracer.log("UI Results Display", f"Processed leads", page.status_label.cget("text"))

if __name__ == "__main__":
    test()
