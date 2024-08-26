from pydantic import BaseModel, Field
from typing import Optional, Dict

class DataSourceRequest(BaseModel):
    dataset_name: str = Field(
        ...,
        description="The unique name of the dataset to be created.",
        json_schema_extra={"example": "example_dataset_name"},
    )
    dataset_title: str = Field(
        ...,
        description="The title of the dataset to be created.",
        json_schema_extra={"example": "Example Dataset Title"},
    )
    owner_org: str = Field(
        ...,
        description="The ID of the organization to which the dataset belongs.",
        json_schema_extra={"example": "example_org_id"},
    )
    resource_url: str = Field(
        ...,
        description="The URL of the resource to be associated with the dataset.",
        json_schema_extra={"example": "http://example.com/resource"},
    )
    resource_name: str = Field(
        ...,
        description="The name of the resource to be associated with the dataset.",
        json_schema_extra={"example": "Example Resource Name"},
    )
    dataset_description: str = Field(
        "",
        description="A description of the dataset.",
        json_schema_extra={"example": "This is an example dataset."},
    )
    resource_description: str = Field(
        "",
        description="A description of the resource.",
        json_schema_extra={"example": "This is an example resource."},
    )
    resource_format: str = Field(
        None,
        description="The format of the resource.",
        json_schema_extra={"example": "CSV"},
    )
    extras: Optional[Dict[str, str]] = Field(
        None,
        description=(
            "Additional metadata to be added to the dataset as extras."
        ),
        json_schema_extra={
            "example": {"key1": "value1", "key2": "value2"}
        },
    )
