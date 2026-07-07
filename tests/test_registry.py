from app.connectors import get_connectors

def test_get_connectors_returns_requested():
    conns = get_connectors(["x", "threads"])
    assert [c.name for c in conns] == ["x", "threads"]

def test_get_connectors_empty():
    assert get_connectors([]) == []