import importlib, os

def test_settings_read_from_env(monkeypatch):
    monkeypatch.setenv("BLUESKY_HANDLE", "me.bsky.social")
    monkeypatch.setenv("BLUESKY_APP_PASSWORD", "secret")
    import app.config as config
    importlib.reload(config)
    assert config.settings.bluesky_handle == "me.bsky.social"
    assert config.settings.bluesky_app_password == "secret"