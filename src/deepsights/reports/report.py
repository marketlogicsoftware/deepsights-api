import time
from deepsights.api import DeepSights
from deepsights.reports._model import Report


#################################################
def report_create(api: DeepSights, question: str) -> str:
    """
    Creates a new report by submitting a question to the DeepSights API.

    Args:
        api (DeepSights): An instance of the DeepSights API client.
        question (str): The question to be submitted for the report.

    Returns:
        str: The ID of the created report's minion job.
    """

    body = {"input": question}
    response = api.post(
        "/minion-commander-service/desk-researches", body=body, timeout=5
    )

    return response["minion_job"]["id"]


#################################################
def report_wait_for_completion(api: DeepSights, report_id: str, timeout=600):
    """
    Waits for the completion of a report.

    Args:
        api (DeepSights): The DeepSights API instance.
        report_id (str): The ID of the report.
        timeout (int, optional): The maximum time to wait for the report to complete, in seconds. Defaults to 600.

    Raises:
        ValueError: If the report fails to complete.

    Returns:
        None
    """
    # wait for completion
    start = time.time()
    while time.time() - start < timeout:
        response = api.get(f"/minion-commander-service/desk-researches/{report_id}")["minion_job"]

        if response["status"] in ("CREATED", "STARTED"):
            time.sleep(2)
        elif response["status"].startswith("FAILED"):
            raise ValueError(
                f"Report {report_id} failed to complete: {response['error_reason']}"
            )
        else:
            return

    raise ValueError(f"Report {report_id} failed to complete within {timeout} seconds.")


#################################################
def report_get(api: DeepSights, report_id: str) -> Report:
    """
    Loads a report from the DeepSights API.

    Args:
        api (DeepSights): An instance of the DeepSights API client.
        report_id (str): The ID of the report to load.

    Returns:
        Report: The loaded report.
    """
    response = api.get(f"/minion-commander-service/desk-researches/{report_id}")

    return Report(
        **dict(
            id=response["minion_job"]["id"],
            status=response["minion_job"]["status"],
            question=response["context"]["input"],
            language=response["context"]["input_language"],
            topic=response["context"]["topic"],
            summary=response["context"]["summary"],
            document_sources=response["context"]["artifact_vector_search_results"],
            news_sources=response["context"]["scs_news_search_results"],
        )
    )
