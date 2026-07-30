# Troubleshooting LeadForge AI

## 1. Chromium Fails to Install
If you click "Generate Sales Package" and the Chromium installer fails:
- Check your internet connection.
- Ensure you have ~150MB of free disk space.
- Run the application as Administrator.
- Alternatively, open a terminal and run `pip install playwright` followed by `playwright install chromium`.

## 2. No Results from Lead Generator
- OpenStreetMap limits queries. If you search for an extremely large area (e.g., "United States"), the query will timeout. Always search by City or Zip Code.
- Try increasing the Search Radius in the **Settings** menu.

## 3. Website Analyzer Fails
- Some websites block automated scrapers. LeadForge AI uses custom User-Agents and Retries, but Cloudflare or advanced WAFs may still block access.
- If the website is dead, the lead score will remain low.

## 4. Map View Not Loading
- The Map View uses OpenStreetMap tiles. Ensure your firewall is not blocking `a.tile.openstreetmap.org`.
