import pytest
import requests
import deepsights


def test_documents_delete_404():
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        deepsights.documents_delete(
            deepsights.DeepSights(),
            ["aaa"],
        )

    assert exc.value.response.status_code == 404
