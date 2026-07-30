# Contributing to LeadForge AI

## Architecture
LeadForge AI follows a service-oriented architecture separating UI, Business Logic, and Data.

- `core/`: Configurations, logger, global task manager, and robust network session handling.
- `database/`: SQLAlchemy ORM models (`models/lead.py`) and schema management.
- `exports/`: Output generators (CSV, Excel, PDF).
- `services/`: Independent workers (`analyzer.py`, `screenshot_engine.py`, `ai_generators.py`, `providers.py`).
- `ui/`: CustomTkinter GUI separated by Pages.

## Adding a new Provider
1. Inherit from `BaseProvider` in `services/providers.py`.
2. Implement `search_leads(query, location, radius, max)`.
3. Register the new provider string in `ui/pages/settings.py`.

## UI Guidelines
- Do NOT run heavy I/O operations on the main thread. Always dispatch to `task_manager.add_task()`.
- Use `toast_manager` for notifications instead of blocking message boxes.
- Keep the `CustomTkinter` design consistent by using constants from `core.config.COLORS`.
