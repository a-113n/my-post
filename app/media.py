from io import BytesIO
from PIL import Image

def to_png_bytes(data: bytes) -> bytes:
    img = Image.open(BytesIO(data))
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()