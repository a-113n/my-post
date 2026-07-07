from pathlib import Path
from app.media import to_png_bytes

FIXTURE = Path(__file__).parent / "fixtures" / "sample.jpg"

def test_to_png_bytes_returns_png_signature():
    png = to_png_bytes(FIXTURE.read_bytes())
    assert png[:8] == b"\x89PNG\r\n\x1a\n"  # PNG file signature