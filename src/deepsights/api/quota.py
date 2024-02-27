from deepsights.api.api import DeepSights
from deepsights.api._model import APIProfile, QuotaStatus


#################################################
def api_get_profile(api: DeepSights):
    """
    Retrieves the API key attributes from the DeepSights API.

    Args:
        api (ds.DeepSights): The DeepSights API instance.

    Returns:
        APIKeyAttributes: The parsed API key attributes.
    """
    response = api.get("/static-resolver/api-key-attributes")
    return APIProfile.model_validate(response)


#################################################
def quota_get_status(api: DeepSights):
    """
    Get the quota status from the DeepSights API.

    Args:
        api (DeepSights): The DeepSights API object.

    Returns:
        QuotaStatus: The validated quota status response.
    """
    response = api.get("/static-resolver/quota")
    return QuotaStatus.model_validate(response)
