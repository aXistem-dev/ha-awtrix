from __future__ import annotations

import json
import struct
import unittest
import zlib

from tests._load import screen


def decode_png(data: bytes):
    """Minimal decoder for the PNGs ``to_png`` writes: returns (width, height, rows of RGB bytes)."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, size = 8, b"", None
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        kind, body = data[pos + 4 : pos + 8], data[pos + 8 : pos + 8 + length]
        (crc,) = struct.unpack(">I", data[pos + 8 + length : pos + 12 + length])
        assert crc == zlib.crc32(kind + body) & 0xFFFFFFFF, kind
        if kind == b"IHDR":
            size = struct.unpack(">II", body[:8])
            assert body[8:] == bytes([8, 2, 0, 0, 0])
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
    raw = zlib.decompress(idat)
    width, height = size
    stride = 1 + width * 3
    assert len(raw) == height * stride
    rows = []
    for y in range(height):
        assert raw[y * stride] == 0
        rows.append(raw[y * stride + 1 : (y + 1) * stride])
    return width, height, rows


class ParseTests(unittest.TestCase):
    def test_valid(self):
        payload = json.dumps({"width": 2, "height": 2, "pixels": [0, 255, 65280, 16711680]})
        self.assertEqual(screen.parse_screen(payload), (2, 2, [0, 255, 65280, 16711680]))

    def test_unusable(self):
        bad = [
            None,
            "",
            "nope",
            "[]",
            '{"width":2,"height":2,"pixels":[1,2,3]}',
            '{"width":2,"height":2,"pixels":[1,2,3,"x"]}',
            '{"width":2,"height":2,"pixels":[1,2,3,16777216]}',
            '{"width":0,"height":2,"pixels":[]}',
            '{"width":1000,"height":1000,"pixels":[]}',
        ]
        for payload in bad:
            self.assertIsNone(screen.parse_screen(payload), payload)


class PngTests(unittest.TestCase):
    def test_size_and_pixels(self):
        png = screen.to_png(2, 1, [0xFF0000, 0x0000FF], scale=4, gap=1)
        width, height, rows = decode_png(png)
        self.assertEqual((width, height), (8, 4))
        red, blue, black = b"\xff\x00\x00", b"\x00\x00\xff", b"\x00\x00\x00"
        self.assertEqual(rows[0], red * 3 + black + blue * 3 + black)
        self.assertEqual(rows[2], rows[0])
        self.assertEqual(rows[3], black * 8)  # the gap row

    def test_no_gap(self):
        _, _, rows = decode_png(screen.to_png(1, 1, [0x123456], scale=2, gap=0))
        self.assertEqual(rows, [b"\x12\x34\x56" * 2] * 2)

    def test_default_matrix_size(self):
        width, height, _ = decode_png(screen.to_png(32, 8, [0] * 256))
        self.assertEqual((width, height), (256, 64))


if __name__ == "__main__":
    unittest.main()
