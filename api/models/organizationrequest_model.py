from pydantic import BaseModel, Field
from typing import Optional

class OrganizationRequest(BaseModel):
    name: str = Field(
        ...,
        json_schema_extra={
            "example": "example_org_name",
            "description": "The unique name of the organization to be created.",
        },
    )
    title: str = Field(
        ...,
        json_schema_extra={
            "example": "Example Organization Title",
            "description": "The title of the organization to be created.",
        },
    )
    description: Optional[str] = Field(
        None,
        json_schema_extra={
            "example": "This is an example organization.",
            "description": "A description of the organization.",
        },
    )
