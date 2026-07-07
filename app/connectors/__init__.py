from .base import Connector
from .x import XConnector
from .threads import ThreadsConnector
from .instagram import InstagramConnector
from .bluesky import BlueskyConnector

# Bluesky registered; uses real atproto client when no client is injected.
REGISTRY = {
    "x": XConnector,
    "threads": ThreadsConnector,
    "instagram": InstagramConnector,
    "bluesky": BlueskyConnector,
}

def get_connectors(names: list[str]) -> list[Connector]:
    return [REGISTRY[n]() for n in names if n in REGISTRY]