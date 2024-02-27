from typing import List
from deepsights.api import DeepSights
from deepsights.answers._model import DocumentAnswer


#################################################
def answers_get(api: DeepSights, question: str, timeout=30) -> List[DocumentAnswer]:
    """
    Retrieves answers for a given question.

    Args:
        api (DeepSights): The DeepSights API client.
        question (str): The question to retrieve answers for.
        timeout (int, optional): The timeout for the request. Defaults to 30.

    Returns:
        List[DocumentAnswer]: The list of answers for the question.
    """

    body = {"search_term": question}
    response = api.post("/answer-service/answer-sets", body=body, timeout=timeout)

    return [DocumentAnswer.model_validate(answer) for answer in response["answers"]]
