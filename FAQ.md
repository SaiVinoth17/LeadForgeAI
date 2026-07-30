# Frequently Asked Questions

**Q: Do I need to pay for Google API Keys?**
A: No! Version 2.0 replaced Google APIs with OpenStreetMap, making LeadForge AI completely free to use.

**Q: How does the AI Lead Score work?**
A: The system deducts points from 100 for missing features (e.g., no SSL, missing H1 tags, no mobile responsiveness). A lower score means the business is a prime candidate for a website redesign.

**Q: Where are my screenshots saved?**
A: Screenshots are cached in the `data/screenshots/` folder within the application directory. They automatically expire after 7 days.

**Q: Can I customize the Email templates?**
A: The AI Generators use dynamic string formatting. To modify them fundamentally, edit `services/ai_generators.py` before building the executable.
