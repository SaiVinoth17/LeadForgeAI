import os
import time
import threading
from PIL import ImageGrab
from app import App
from database.crud import get_all_leads

# Disable os.startfile to prevent explorer windows from popping up
os.startfile = lambda x: print(f"Mock startfile for {x}")

def take_screenshot(name):
    # take screenshot
    time.sleep(1)
    try:
        img = ImageGrab.grab()
        artifact_path = f"C:\\Users\\user\\.gemini\\antigravity\\brain\\e80d6729-5bf0-4f7b-a675-056920eae8e9\\{name}.png"
        img.save(artifact_path)
        print(f"Screenshot saved: {artifact_path}")
    except Exception as e:
        print(f"Screenshot failed: {e}")

def run_e2e_tests(app):
    print("Starting E2E tests...")
    time.sleep(2)
    
    # 1. Lead Generator
    print("Navigating to Lead Generator...")
    app.main_window.show_page("lead_generator")
    app.update()
    time.sleep(1)
    
    page = app.main_window.pages["lead_generator"]
    
    # Search 1: Hotel -> Ooty
    page.query_var.set("Hotel")
    page.location_var.set("Ooty")
    print("Searching Hotel -> Ooty...")
    page.on_search()
    wait_for_search(app, page)
    take_screenshot("lead_gen_ooty")
    
    # Search 2: Restaurant -> Coimbatore
    page.query_var.set("Restaurant")
    page.location_var.set("Coimbatore")
    print("Searching Restaurant -> Coimbatore...")
    page.on_search()
    wait_for_search(app, page)
    
    # Search 3: Plumber -> Bangalore
    page.query_var.set("Plumber")
    page.location_var.set("Bangalore")
    print("Searching Plumber -> Bangalore...")
    page.on_search()
    wait_for_search(app, page)
    
    # Duplicate Detection
    print("Testing duplicate detection (Hotel -> Ooty again)...")
    page.query_var.set("Hotel")
    page.location_var.set("Ooty")
    page.on_search()
    wait_for_search(app, page)
    
    # 2. CRM
    print("Navigating to CRM...")
    app.main_window.show_page("crm")
    app.update()
    time.sleep(1)
    take_screenshot("crm_view")
    
    # 3. Exports
    print("Testing Exports...")
    crm_page = app.main_window.pages["crm"]
    crm_page.export_csv()
    crm_page.export_excel()
    crm_page.export_pdf()
    take_screenshot("crm_exports")
    
    # 4. Analyzer
    print("Navigating to Analyzer...")
    app.main_window.show_page("analyzer")
    app.update()
    time.sleep(1)
    analyzer_page = app.main_window.pages["analyzer"]
    
    leads = get_all_leads()
    websites = [l.website for l in leads if l.website and l.website.startswith('http')]
    websites = list(set(websites))[:3]
    if len(websites) < 3:
        websites.extend(["https://reactjs.org", "https://www.djangoproject.com", "https://vuejs.org"][:3-len(websites)])
        
    for i, w in enumerate(websites):
        print(f"Analyzing {w}...")
        analyzer_page.url_var.set(w)
        analyzer_page.on_analyze()
        for _ in range(40):
            app.update()
            time.sleep(1)
            if analyzer_page.analyze_btn.cget("state") == "normal":
                break
        take_screenshot(f"analyzer_{i}")
        
    print("Tests complete. Closing app.")
    app.destroy()

def wait_for_search(app, page):
    for _ in range(40):
        app.update()
        time.sleep(1)
        if page.search_btn.cget("state") == "normal":
            break

if __name__ == "__main__":
    app = App()
    threading.Thread(target=run_e2e_tests, args=(app,), daemon=True).start()
    app.mainloop()
