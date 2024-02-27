from typing import Optional
from pydantic import BaseModel, Field, AliasChoices


#################################################
class DeepSightsBaseModel(BaseModel):
    """
    Represents the base model for all DeepSights models.
    """

    #############################################
    def schema_human(self) -> str:
        """
        Returns a simplified human-readable string representation of the model's schema.

        The schema includes the field names, types, and descriptions.

        Returns:
            str: The model's schema.
        """
        return "\n".join(
            [
                f"{field_name} ({field.annotation}): {field.description}"
                for field_name, field in self.__class__.model_fields.items()
            ]
        )


#################################################
class DeepSightsIdModel(DeepSightsBaseModel):
    """
    Represents the base model for all DeepSights models with an id.
    """

    id: str = Field(
        validation_alias=AliasChoices("id", "item_id", "artifact_id", "page_id", "document_id"),
        description="The ID of the item.",
    )

    #############################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.id}"


#################################################
class DeepSightsIdTitleModel(DeepSightsIdModel):
    """
    Represents the base model for all DeepSights models with an id and title.
    """

    title: Optional[str] = Field(
        validation_alias=AliasChoices("ai_generated_title", "title"),
        description="The human-readable title of the item.",
    )

    #############################################
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}@{self.id}: {self.title}"
