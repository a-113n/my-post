from .base import Connector
from .x import XConnector
from .threads import ThreadsConnector
from .instagram import InstagramConnector

# Bluesky is registered in Phase 3 (needs settings); keep it out for now.
REGISTRY = {
    "x": XConnector,
    "threads": ThreadsConnector,
    "instagram": InstagramConnector,
}

def get_connectors(names: list[str]) -> list[Connector]:
    return [REGISTRY[n]() for n in names if n in REGISTRY]