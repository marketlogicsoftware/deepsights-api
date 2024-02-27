from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from deepsights.api.api import DeepSights


##################################################
# GET API ATTRIBUTES
##################################################


class APIKeyAttributes(BaseModel):
    """
    Represents the attributes of an API key.

    Attributes:
        app (str): The name of the application associated with the API key.
        tenant (str): The tenant ID associated with the API key.
        user (Optional[str]): The user ID associated with the API key (optional).
        daily_quota_limit (Optional[int]): The daily quota limit for the API key (optional).
        minute_quota_limit (Optional[int]): The minute quota limit for the API key (optional).
    """

    app: str
    tenant: str
    user: Optional[str]
    day_quota: Optional[int] = Field(alias="daily_quota_limit")
    minute_quota: Optional[int] = Field(alias="minute_quota_limit")


def get_api_attributes(api: DeepSights):
    """
    Retrieves the API key attributes from the DeepSights API.

    Args:
        api (ds.DeepSights): The DeepSights API instance.

    Returns:
        APIKeyAttributes: The parsed API key attributes.
    """
    response = api.get("/static-resolver/api-key-attributes")
    return APIKeyAttributes.model_validate(response)


##################################################
# QUOTA
##################################################


class QuotaInfo(BaseModel):
    """
    Represents information about a quota.

    Attributes:
        quota (Optional[int]): The quota limit.
        quota_used (Optional[int]): The amount of quota used.
        quota_reset_at (datetime): The date and time when the quota will be reset.
    """

    quota: Optional[int] = Field(alias="quota_limit")
    quota_used: Optional[int]
    quota_reset_at: datetime


class QuotaStatus(BaseModel):
    """
    Represents the quota status for a user.

    Attributes:
        day_quota (QuotaInfo): The daily quota information.
        minute_quota (QuotaInfo): The minute quota information.
    """

    day_quota: QuotaInfo = Field(alias="daily")
    minute_quota: QuotaInfo = Field(alias="minute")


def get_quota_info(api: DeepSights):
    """
    Get the quota information from the DeepSights API.

    Args:
        api (DeepSights): The DeepSights API object.

    Returns:
        QuotaStatus: The validated quota status response.
    """
    response = api.get("/static-resolver/quota")
    return QuotaStatus.model_validate(response)
