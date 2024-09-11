from pydantic import BaseModel, Field
from typing import Optional, Dict

class S3Request(BaseModel):
    resource_name: str = Field(
        ...,
        description="The unique name of the resource to be created.",
        json_schema_extra={"example": "example_resource_name"},
    )
    resource_title: str = Field(
        ...,
        description="The title of the resource to be created.",
        json_schema_extra={"example": "Example Resource Title"},
    )
    owner_org: str = Field(
        ...,
        description="The ID of the organization to which the resource belongs.",
        json_schema_extra={"example": "example_org_id"},
    )
    resource_s3: str = Field(
        ...,
        description="The S3 URL of the resource to be added.",
        json_schema_extra={"example": "http://example.com/resource"},
    )
    notes: str = Field(
        "",
        description="Additional notes about the resource.",
        json_schema_extra={"example": "Additional notes about the resource."},
    )
    extras: Optional[Dict[str, str]] = Field(
        None,
        description="Additional metadata to be added to the resource package as extras.",
        json_schema_extra={"example": {"key1": "value1", "key2": "value2"}},
    )
