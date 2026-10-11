"""Turn the AWTRIX NG screen snapshot into a PNG.

``<prefix>/cmd/screen/get`` makes the firmware publish ``{"width": W, "height": H, "pixels": [...]}`` on
``<prefix>/state/screen``, one packed 0xRRGGBB integer per pixel. The picture is drawn like the LED matrix:
every pixel is a square block with a dark gap around it. Pure Python, no Home Assistant imports.
"""

from __future__ import annotations

import json
import struct
import zlib
from typing import Any

MAX_PIXELS = 128 * 8 * 4  # the panel is at most 128 x 8; leave headroom


def parse_screen(payload: str | bytes | None) -> tuple[int, int, list[int]] | None:
    """Return ``(width, height, pixels)`` from a ``state/screen`` payload, or ``None`` if it is unusable."""
    if not payload:
        return None
    try:
        data: Any = json.loads(payload)
    except (TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    width, height, pixels = data.get("width"), data.get("height"), data.get("pixels")
    if not (isinstance(width, int) and isinstance(height, int) and isinstance(pixels, list)):
        return None
    if width < 1 or height < 1 or width * height > MAX_PIXELS or len(pixels) != width * height:
        return None
    if not all(isinstance(p, int) and 0 <= p <= 0xFFFFFF for p in pixels):
        return None
    return width, height, pixels


def _chunk(kind: bytes, body: bytes) -> bytes:
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def to_png(width: int, height: int, pixels: list[int], scale: int = 8, gap: int = 1) -> bytes:
    """Encode the pixels as an RGB PNG, each pixel ``scale`` x ``scale`` with a ``gap`` of black on its right and bottom."""
    scale = max(1, scale)
    gap = max(0, min(gap, scale - 1))
    rows = []
    for y in range(height):
        line = bytearray()
        for x in range(width):
            value = pixels[y * width + x]
            lit = bytes(((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF))
            cell = lit * (scale - gap) + b"\x00\x00\x00" * gap
            line += cell
        for dy in range(scale):
            rows.append(b"\x00" + (bytes(line) if dy < scale - gap else b"\x00" * len(line)))
    raw = b"".join(rows)
    header = struct.pack(">IIBBBBB", width * scale, height * scale, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b"")
