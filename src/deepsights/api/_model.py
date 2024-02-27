from typing import Optional
from datetime import datetime
from pydantic import Field
from deepsights.utils import DeepSightsBaseModel


#################################################
class APIProfile(DeepSightsBaseModel):
    """
    Represents the profile of an API key.

    Attributes:
        app (str): The name of the application associated with the API key.
        tenant (str): The name of the tenant associated with the API key.
        user (Optional[str]): The user ID associated with the API key.
        day_quota (Optional[int]): The daily request quota limit for the API key.
        minute_quota (Optional[int]): The minute request quota limit for the API key.
    """

    app: str = Field(
        description="The name of the application associated with the API key."
    )
    tenant: str = Field(
        description="The name of the tenant associated with the API key."
    )
    user: Optional[str] = Field(description="The user ID associated with the API key.")
    day_quota: Optional[int] = Field(
        alias="daily_quota_limit",
        description="The daily request quota limit for the API key; if None, unlimited.",
    )
    minute_quota: Optional[int] = Field(
        alias="minute_quota_limit",
        description="The minute request quota limit for the API key; if None, unlimited.",
    )


#################################################
class QuotaInfo(DeepSightsBaseModel):
    """
    Represents information about the quota for API requests.

    Attributes:
        quota (Optional[int]): The request quota limit.
        quota_used (Optional[int]): The number of requests used.
        quota_reset_at (datetime): The time at which the quota will be reset.
    """

    quota: Optional[int] = Field(
        alias="quota_limit",
        description="The request quota limit per time period; if None, unlimited.",
    )
    quota_used: Optional[int] = Field(
        description="The number of requests used in this time period."
    )
    quota_reset_at: datetime = Field(
        description="The time at which the quota will be reset."
    )


#################################################
class QuotaStatus(DeepSightsBaseModel):
    """
    Represents the quota status for the API.

    Attributes:
        day_quota (QuotaInfo): The daily quota limit and status.
        minute_quota (QuotaInfo): The minute quota limit and status.
    """

    day_quota: QuotaInfo = Field(
        alias="daily", description="The daily quota limit and status."
    )
    minute_quota: QuotaInfo = Field(
        alias="minute", description="The minute quota limit and status."
    )
