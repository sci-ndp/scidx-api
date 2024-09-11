from typing import Optional, Dict
from pydantic import BaseModel, Field

class S3ResourceUpdateRequest(BaseModel):
    resource_name: Optional[str] = Field(
        None,
        description="The unique name of the resource.",
        json_schema_extra={"example": "example_resource_name"},
    )
    resource_title: Optional[str] = Field(
        None,
        description="The title of the resource.",
        json_schema_extra={"example": "Example Resource Title"},
    )
    owner_org: Optional[str] = Field(
        None,
        description="The ID of the organization to which the resource belongs.",
        json_schema_extra={"example": "example_org_id"},
    )
    resource_s3: Optional[str] = Field(
        None,
        description="The S3 URL of the resource.",
        json_schema_extra={"example": "http://example.com/resource"},
    )
    notes: Optional[str] = Field(
        None,
        description="Additional notes about the resource.",
        json_schema_extra={"example": "Additional notes about the resource."},
    )
    extras: Optional[Dict[str, str]] = Field(
        None,
        description="Additional metadata to be added to the resource package as extras.",
        json_schema_extra={"example": {"key1": "value1", "key2": "value2"}},
    )
