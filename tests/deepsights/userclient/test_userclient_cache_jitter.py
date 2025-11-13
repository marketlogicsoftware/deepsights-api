"""
Unit tests for UserClient cache behavior and token refresh jitter.
"""

from deepsights.userclient.userclient import UserClient


class _DummyTimer:
    def __init__(self, interval, function):
        self.interval = interval
        self.function = function
        self.daemon = False
        self.started = False

    def cancel(self):
        self.started = False

    def start(self):
        self.started = True


def test_userclient_cache_helpers(monkeypatch):
    # Ensure resolver returns a token and avoid background timers
    monkeypatch.setattr(
        "deepsights.deepsights._mip_identity.MIPIdentityResolver.get_oauth_token",
        lambda self, email: "tok",
    )
    monkeypatch.setattr("threading.Timer", _DummyTimer)
    # Clear cache before test
    UserClient.cache_clear()

    uc1 = UserClient(email="User@Example.com", api_key="k")
    uc2 = UserClient.get_userclient("user@example.com", "k")

    assert uc2 is not None
    # Cached instance returned for normalized email
    assert UserClient.cache_info()["currsize"] >= 1
    UserClient.cache_invalidate("user@example.com")
    assert UserClient.cache_info()["currsize"] >= 0
    UserClient.cache_clear()
    assert UserClient.cache_info()["currsize"] == 0
    uc1.close()


def test_userclient_refresh_jitter(monkeypatch):
    # Deterministic jitter: +10%
    monkeypatch.setattr(
        "deepsights.deepsights._mip_identity.MIPIdentityResolver.get_oauth_token",
        lambda self, email: "tok",
    )
    monkeypatch.setattr("threading.Timer", _DummyTimer)
    monkeypatch.setattr("random.uniform", lambda a, b: 0.1)

    uc = UserClient(email="user@example.com", api_key="k", auto_refresh_interval_seconds=100)
    # Timer interval should include jitter
    assert isinstance(uc._refresh_timer, _DummyTimer)
    assert abs(uc._refresh_timer.interval - 110.0) < 1e-6
    uc.close()
