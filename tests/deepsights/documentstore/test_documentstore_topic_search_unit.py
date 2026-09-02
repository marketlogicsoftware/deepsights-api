from deepsights.api.resource import APIResource
from deepsights.documentstore.resources.documents._model import TaxonomyFilter
from deepsights.documentstore.resources.documents._search import topic_search


class _DummyAPI:
    def __init__(self):
        self.path = None
        self.body = None

    def post(self, path, params=None, body=None, timeout=None, expected_statuscodes=None):
        self.path = path
        self.body = body
        return {"context": {"search_results": []}}


def test_topic_search_sends_content_type_filter():
    api = _DummyAPI()
    resource = APIResource(api=api)

    results = topic_search(resource, "packaging trends", content_types=["atlas_article"])

    assert results == []
    assert api.path == "supercharged-search-service/topic-searches"
    assert api.body == {
        "query": "packaging trends",
        "extended_search": False,
        "content_type_filter": {"content_types": ["atlas_article"]},
    }


def test_topic_search_combines_taxonomy_and_content_type_filters():
    api = _DummyAPI()
    resource = APIResource(api=api)

    topic_search(
        resource,
        "packaging trends",
        extended_search=True,
        taxonomy_filters=[TaxonomyFilter(field="taxonomy-id", values=["taxon-id"])],
        content_types=["atlas_article", "standalone_document"],
    )

    assert api.body == {
        "query": "packaging trends",
        "extended_search": True,
        "taxonomy_filters": [{"field": "taxonomy-id", "values": ["taxon-id"]}],
        "content_type_filter": {"content_types": ["atlas_article", "standalone_document"]},
    }
