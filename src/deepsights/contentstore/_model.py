from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ContentStoreSearchResult(BaseModel):
    """
    Represents a search result from the content store.

    Attributes:
        id (str): The ID of the item.
        title (str): The title of the item.
        description (str): The description of the item.
        image_url (str): The URL of the item's image.
        url (str): The URL of the item.
        timestamp (Optional[datetime], optional): The timestamp of the item's publication. Defaults to None.
        source (Optional[str], optional): The source of the item. Defaults to None.
    """

    id: str
    title: str
    description: str
    image_url: str
    url: str
    timestamp: Optional[datetime] = Field(alias="published_at", default=None)
    source: dict

    rank: Optional[int] = None
    score_rank: Optional[int] = None
    age_rank: Optional[int] = None

    @property
    def source_name(self) -> str:
        return self.source.get("display_name")

    def __repr__(self) -> str:
        return f"ContentStoreSearchResult@{self.id} - {self.title}"


class NewsSearchResult(ContentStoreSearchResult):
    """
    Represents a search result of a news article in the content store.
    """

    def __repr__(self) -> str:
        return f"NewsSearchResult@{self.id} - {self.title}"


class SecondarySearchResult(ContentStoreSearchResult):
    """
    Represents a search result of a secondary report in the DeepSights API.
    """

    def __repr__(self) -> str:
        return f"SecondarySearchResult@{self.id} - {self.title}"
