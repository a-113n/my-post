from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Sequence, runtime_checkable

@dataclass
class Media:
    data: bytes
    filename: str
    content_type: str = "application/octet-stream"

@dataclass
class Handoff:
    """A copy/paste handoff: open a URL and stage clipboard content."""
    url: str
    instructions: list[str] = field(default_factory=list)
    clipboard_text: str | None = None
    clipboard_image_png: bytes | None = None  # PNG bytes ready for the clipboard

@dataclass
class Result:
    platform: str
    posted: bool                       # True = actually posted (API); False = handoff or error
    handoff: Handoff | None = None
    url: str | None = None             # live post URL when posted
    error: str | None = None

@runtime_checkable
class Connector(Protocol):
    name: str
    def post(self, text: str, media: Sequence[Media] = ()) -> Result: ...