from .base import Result, Handoff

class InstagramConnector:
    name = "instagram"
    COMPOSE_URL = "https://www.instagram.com/"  # VERIFY at build time — IG has no documented share-intent URL

    def post(self, text: str, media=()) -> Result:
        return Result(
            platform=self.name,
            posted=False,
            handoff=Handoff(
                url=self.COMPOSE_URL,
                clipboard_text=text,
                clipboard_image_png=media[0].data if media else None,
                instructions=[
                    "Open Instagram.",
                    "Copy text, paste into the composer.",
                    "Copy image, paste into the composer.",
                    "Click Post on Instagram.",
                ],
            ),
        )