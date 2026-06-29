"""
Backward-compatible re-export.

Existing modules import from app.core.config — this file delegates
to the canonical app.config.settings module (Clean Architecture).
"""

from app.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
