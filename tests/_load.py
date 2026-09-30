"""Load the pure modules without importing Home Assistant (the package __init__ needs it)."""

from __future__ import annotations

import sys
import types
from pathlib import Path

_PACKAGE = "awtrix_pure"
_DIR = Path(__file__).resolve().parent.parent / "custom_components" / "awtrix"

if _PACKAGE not in sys.modules:
    package = types.ModuleType(_PACKAGE)
    package.__path__ = [str(_DIR)]
    sys.modules[_PACKAGE] = package

from awtrix_pure import const, messages, translate  # noqa: E402

__all__ = ["const", "messages", "translate"]
