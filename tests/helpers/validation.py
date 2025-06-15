# Copyright 2024-2025 Market Logic Software AG. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Validation helpers for test assertions.
"""


def assert_valid_document_result(doc_result, expect_document=True):
    """
    Validate a document search result has required fields.

    Args:
        doc_result: Document result object to validate.
    """
    assert doc_result.id is not None
    if expect_document:
        assert doc_result.document is not None
    assert doc_result.page_matches is not None
    assert len(doc_result.page_matches) > 0
    assert doc_result.rank is not None

    for page in doc_result.page_matches:
        assert page.id is not None


def assert_valid_document_page_result(page_result):
    """
    Validate a document page search result has required fields.

    Args:
        page_result: Document page result object to validate.
    """
    assert page_result.document_id is not None
    assert page_result.id is not None
    assert page_result.score > 0


def assert_valid_contentstore_result(cs_result):
    """
    Validate a contentstore search result has required fields.

    Args:
        cs_result: Contentstore result object to validate.
    """
    assert cs_result.id is not None
    assert cs_result.source is not None
    assert cs_result.rank is not None


def assert_valid_answer_result(answer):
    """
    Validate an answer result has required fields.

    Args:
        answer: Answer result object to validate.
    """
    assert answer.question is not None
    assert answer.status == "COMPLETED"
    assert answer.permission_validation in ("GRANTED", "GRANTED_WITH_DELETED_CONTENT")
    assert answer.answer is not None
    assert answer.watchouts is not None


def assert_valid_answer_document_sources(document_sources):
    """
    Validate answer document sources have required fields.

    Args:
        document_sources: List of document source objects to validate.
    """
    assert document_sources is not None
    for doc_result in document_sources:
        assert doc_result.id is not None
        assert doc_result.reference is not None
        assert doc_result.synopsis is not None
        assert doc_result.summary is None
        assert doc_result.text is None
        assert doc_result.publication_date is not None

        assert len(doc_result.pages) > 0
        for page in doc_result.pages:
            assert page.id is not None
            assert page.page_number is not None


def assert_valid_answer_document_suggestions(document_suggestions):
    """
    Validate answer document suggestions have required fields.

    Args:
        document_suggestions: List of document suggestion objects to validate.
    """
    assert document_suggestions is not None
    for doc_result in document_suggestions:
        assert doc_result.id is not None
        assert doc_result.reference is None
        assert doc_result.synopsis is not None
        assert doc_result.summary is None
        assert doc_result.text is None
        assert doc_result.publication_date is not None

        assert len(doc_result.pages) > 0
        for page in doc_result.pages:
            assert page.id is not None
            assert page.page_number is not None


def assert_valid_answer_contentstore_sources(cs_sources):
    """
    Validate answer contentstore sources have required fields.

    Args:
        cs_sources: List of contentstore source objects to validate.
    """
    assert cs_sources is not None
    for cs_result in cs_sources:
        assert cs_result.id is not None
        assert cs_result.reference is not None
        assert cs_result.synopsis is None
        assert cs_result.summary is None
        assert cs_result.text is not None
        assert cs_result.source is not None
        assert cs_result.publication_date is not None


def assert_valid_answer_contentstore_suggestions(cs_suggestions):
    """
    Validate answer contentstore suggestions have required fields.

    Args:
        cs_suggestions: List of contentstore suggestion objects to validate.
    """
    assert cs_suggestions is not None
    for cs_result in cs_suggestions:
        assert cs_result.id is not None
        assert cs_result.reference is None
        assert cs_result.synopsis is None
        assert cs_result.summary is None
        assert cs_result.text is not None
        assert cs_result.source is not None
        assert cs_result.publication_date is not None


def assert_valid_report_result(report):
    """
    Validate a report result has required fields.

    Args:
        report: Report result object to validate.
    """
    assert report.permission_validation in ("GRANTED", "GRANTED_WITH_DELETED_CONTENT")
    assert report.question is not None
    assert report.status == "COMPLETED"
    assert report.topic is not None
    assert report.summary is not None


def assert_valid_report_document_sources(document_sources):
    """
    Validate report document sources have required fields.

    Args:
        document_sources: List of document source objects to validate.
    """
    assert document_sources is not None
    assert len(document_sources) > 0
    for doc in document_sources:
        assert doc.id is not None
        assert doc.reference is not None
        assert doc.synopsis is not None
        assert doc.summary is not None
        assert doc.publication_date is not None

        assert len(doc.pages) > 0
        for page in doc.pages:
            assert page.id is not None
            assert page.page_number is not None


def assert_valid_report_contentstore_sources(cs_sources):
    """
    Validate report contentstore sources have required fields.

    Args:
        cs_sources: List of contentstore source objects to validate.
    """
    assert cs_sources is not None
    assert len(cs_sources) > 0
    for cs_result in cs_sources:
        assert cs_result.id is not None
        assert cs_result.reference is not None
        assert cs_result.synopsis is None
        assert cs_result.summary is not None
        assert cs_result.text is None
        assert cs_result.source is not None
        assert cs_result.publication_date is not None


def assert_valid_quota_profile(profile):
    """
    Validate a quota profile has required fields.

    Args:
        profile: Quota profile object to validate.
    """
    assert profile.app is not None
    assert profile.tenant is not None


def assert_valid_quota_status(status):
    """
    Validate a quota status has required fields.

    Args:
        status: Quota status object to validate.
    """
    assert status.day_quota is not None
    assert status.day_quota.quota_reset_at is not None
    assert status.day_quota.quota_used >= 0

    assert status.minute_quota is not None
    assert status.minute_quota.quota_reset_at is not None
    assert status.minute_quota.quota_used >= 0


def assert_ranked_results(results):
    """
    Validate that results are properly ranked in ascending order.

    Args:
        results: List of result objects with rank attribute.
    """
    for ix, result in enumerate(results):
        assert result.rank == ix + 1


def assert_descending_scores(results):
    """
    Validate that results are sorted by score in descending order.

    Args:
        results: List of result objects with score attribute.
    """
    for ix, result in enumerate(results):
        if ix > 0:
            assert result.score <= results[ix - 1].score


def assert_valid_topic_search_result(topic_result):
    """
    Validate a topic search result has required fields.

    Args:
        topic_result: Topic search result object to validate.
    """
    assert topic_result.artifact_id is not None
    assert topic_result.artifact_title is not None
    assert topic_result.page_references is not None
    assert len(topic_result.page_references) > 0

    for page_ref in topic_result.page_references:
        assert page_ref.id is not None
        assert page_ref.number is not None
        assert page_ref.number > 0
        assert page_ref.text is not None
        assert page_ref.relevance_class is not None
        assert page_ref.relevance_assessment is not None


def assert_valid_hybrid_search_result(hybrid_result):
    """
    Validate a hybrid search result has required fields.

    Args:
        hybrid_result: Hybrid search result object to validate.
    """
    assert hybrid_result.artifact_id is not None
    assert hybrid_result.artifact_title is not None
    assert hybrid_result.page_references is not None
    assert len(hybrid_result.page_references) > 0

    for page_ref in hybrid_result.page_references:
        assert page_ref.id is not None
        if page_ref.number is not None:
            assert page_ref.number > 0
        assert page_ref.text is not None


def assert_ascending_ranks(results):
    """
    Validate that results have ascending rank values.

    Args:
        results: List of result objects with rank attribute.
    """
    for ix, result in enumerate(results):
        if ix > 0:
            assert result.rank > results[ix - 1].rank


def assert_descending_publication_dates(results):
    """
    Validate that results are sorted by publication date in descending order.

    Args:
        results: List of result objects with publication_date attribute.
    """
    for ix, result in enumerate(results):
        if ix > 0:
            assert result.publication_date <= results[ix - 1].publication_date


def assert_ascending_publication_dates(results):
    """
    Validate that results are sorted by publication date in ascending order.

    Args:
        results: List of result objects with publication_date attribute.
    """
    for ix, result in enumerate(results):
        if ix > 0:
            assert result.publication_date >= results[ix - 1].publication_date


def assert_date_range_filter(results, start_date=None, end_date=None):
    """
    Validate that results fall within specified date range.

    Args:
        results: List of result objects with publication_date attribute.
        start_date: Optional start date for filtering.
        end_date: Optional end date for filtering.
    """
    for result in results:
        if start_date:
            assert result.publication_date >= start_date
        if end_date:
            assert result.publication_date <= end_date


def assert_language_filter(results, expected_languages):
    """
    Validate that results match expected language filters.

    Args:
        results: List of result objects with language attribute.
        expected_languages: List of expected language codes.
    """
    for result in results:
        assert result.language in expected_languages
