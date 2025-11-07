"""
Unit test for API.get_content bytes return.
"""



from deepsights.api.api import API


class _Resp:
    def __init__(self, status, content=b""):
        self.status_code = status
        self.content = content

    def json(self):
        return {}


def test_get_content_returns_bytes(monkeypatch):
    api = API(endpoint_base="https://example.invalid/")

    def fake_get(url, params=None, timeout=None):
        return _Resp(200, b"abc")

    api._session.get = fake_get  # type: ignore[attr-defined]
    assert api.get_content("/bin") == b"abc"

