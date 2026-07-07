from .base import Result
from ..config import settings

class BlueskyConnector:
    name = "bluesky"

    def __init__(self, client=None):
        self._client = client  # inject for tests; None => real atproto client

    def _ensure_client(self):
        if self._client is None:
            from atproto import Client  # imported lazily so tests need no SDK
            c = Client()
            c.login(settings.bluesky_handle, settings.bluesky_app_password)
            self._client = c
        return self._client

    def post(self, text: str, media=()) -> Result:
        try:
            client = self._ensure_client()
            blobs = [client.upload_blob(m.data).blob for m in media[:4]]
            embed = None
            if blobs:
                from atproto import models
                embed = models.AppBskyEmbedImages.Main(
                    images=[models.AppBskyEmbedImages.Image(alt="", image=b) for b in blobs]
                )
            res = client.send_post(text, embed=embed)
            rkey = res.uri.rsplit("/", 1)[-1]
            return Result(
                platform=self.name,
                posted=True,
                url=f"https://bsky.app/profile/{settings.bluesky_handle}/post/{rkey}",
            )
        except Exception as e:  # surface a clean error to the results page
            return Result(platform=self.name, posted=False, error=str(e))