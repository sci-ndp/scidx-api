from pydantic import BaseModel, Field

class S3Request(BaseModel):
    resource_name: str = Field(..., json_schema_extra={"example": "example_resource_name", "description": "The unique name of the resource to be created."})
    resource_title: str = Field(..., json_schema_extra={"example": "Example Resource Title", "description": "The title of the resource to be created."})
    owner_org: str = Field(..., json_schema_extra={"example": "example_org_id", "description": "The ID of the organization to which the resource belongs."})
    resource_s3: str = Field(..., json_schema_extra={"example": "http://example.com/resource", "description": "The S3 to be added."})
    notes: str = Field("", json_schema_extra={"example": "Additional notes about the resource.", "description": "Additional notes about the resource."})
