import json
import deepsights

# get the test data from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    data = json.load(f)
    test_question = data["question"]
    test_report_id = data["report_id"]


def test_report_wait_for_completion():
    deepsights.report_wait_for_completion(deepsights.DeepSights(), test_report_id)


def test_report_get():
    report = deepsights.report_get(deepsights.DeepSights(), test_report_id)

    assert report.id == test_report_id
    assert report.question is not None
    assert report.status == "COMPLETED"
    assert report.language is not None
    assert report.topic is not None
    assert report.summary is not None

    assert report.document_sources is not None
    assert len(report.document_sources) > 0
    for doc in report.document_sources:
        assert doc.id is not None
        assert doc.rating is not None
        assert doc.reference is not None
        assert doc.description is not None
        assert doc.evidence_summary is not None
        assert doc.publication_date is not None

        assert len(doc.pages) > 0
        for page in doc.pages:
            assert page.id is not None
            assert page.page_number is not None

    assert report.news_sources is not None
    assert len(report.news_sources) > 0
    for news in report.news_sources:
        assert news.id is not None
        assert news.description is not None
        assert news.evidence_summary is not None
        assert news.source is not None
        assert news.rating is not None
        assert news.publication_date is not None
