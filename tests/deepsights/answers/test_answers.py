import json
import deepsights

# get the test data from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    data = json.load(f)
    test_question = data["question"]


def test_answers():
    answers = deepsights.answers_get(deepsights.DeepSights(), test_question)

    assert len(answers) > 0
    for answer in answers:
        assert answer.id is not None
        assert answer.artifact_id is not None
        assert answer.artifact_type == "DOCUMENT"
        assert answer.summary is not None
        assert answer.timestamp is not None
        assert answer.pages is not None
        assert len(answer.pages) > 0
        for page in answer.pages:
            assert page.page_id is not None
            assert page.page_number is not None
            assert page.score is not None
            assert page.score >= 0.0
            assert page.score <= 100.0
