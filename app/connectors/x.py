from urllib.parse import quote
from .base import Connector, Result, Handoff

INTENT_URL = "https://twitter.com/intent/tweet"

class XConnector:
    name = "x"

    def post(self, text: str, media=()) -> Result:
        return Result(
            platform=self.name,
            posted=False,
            handoff=Handoff(
                url=f"{INTENT_URL}?text={quote(text)}",
                clipboard_text=None,
                clipboard_image_png=media[0].data if media else None,
                instructions=[
                    "Open X — your text is already filled in.",
                    "Copy image, then paste (Ctrl/Cmd+V) into the composer.",
                    "Click Post on X.",
                ],
            ),
        )