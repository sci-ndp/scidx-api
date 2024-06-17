from pydantic import BaseModel, Field

class OrganizationDeleteRequest(BaseModel):
    organization_id: str = Field(..., json_schema_extra={
        "description": "The ID of the organization to be deleted.",
        "example": "example_org_id"
    })