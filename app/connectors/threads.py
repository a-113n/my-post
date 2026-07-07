from .base import Result, Handoff

class ThreadsConnector:
    name = "threads"
    COMPOSE_URL = "https://www.threads.net/"  # VERIFY at build time — Threads has no documented share-intent URL

    def post(self, text: str, media=()) -> Result:
        return Result(
            platform=self.name,
            posted=False,
            handoff=Handoff(
                url=self.COMPOSE_URL,
                clipboard_text=text,
                clipboard_image_png=media[0].data if media else None,
                instructions=[
                    "Open Threads.",
                    "Copy text, paste into the composer.",
                    "Copy image, paste into the composer.",
                    "Click Post on Threads.",
                ],
            ),
        )