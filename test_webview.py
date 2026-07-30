import webview
import json

class API:
    def get_kpis(self):
        return {
            "leads_forged": 1500,
            "active_scrapers": 1,
            "accuracy": 98,
            "credits": 5000
        }

def start_webview():
    api = API()
    window = webview.create_window('LeadForge AI Command Center', 'command_center.html', js_api=api, width=1280, height=800)
    webview.start()

if __name__ == '__main__':
    start_webview()
