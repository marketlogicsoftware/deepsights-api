import pytest
import requests
import deepsights


def test_ds_api_authentication():
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        deepsights.api_get_profile(deepsights.DeepSights(api_key="1234567890"))

    assert exc.value.response.status_code == 401


def test_cs_api_authentication():
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        deepsights.api_get_profile(deepsights.ContentStore(api_key="1234567890"))

    assert exc.value.response.status_code == 401


def test_ds_api_attributes():
    r = deepsights.api_get_profile(deepsights.DeepSights())

    assert r.app is not None
    assert r.tenant is not None


def test_ds_quota_info():
    r = deepsights.quota_get_status(deepsights.DeepSights())

    assert r.day_quota is not None
    assert r.day_quota.quota_reset_at is not None
    assert r.day_quota.quota_used >= 0

    assert r.minute_quota is not None
    assert r.minute_quota.quota_reset_at is not None
    assert r.minute_quota.quota_used >= 0
