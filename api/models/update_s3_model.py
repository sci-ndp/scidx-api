from typing import Optional, Dict
from pydantic import BaseModel, Field

class S3ResourceUpdateRequest(BaseModel):
    resource_name: Optional[str] = Field(None, example="example_resource_name", description="The unique name of the resource.")
    resource_title: Optional[str] = Field(None, example="Example Resource Title", description="The title of the resource.")
    owner_org: Optional[str] = Field(None, example="example_org_id", description="The ID of the organization to which the resource belongs.")
    resource_s3: Optional[str] = Field(None, example="http://example.com/resource", description="The S3 URL of the resource.")
    notes: Optional[str] = Field(None, example="Additional notes about the resource.", description="Additional notes about the resource.")
    extras: Optional[Dict[str, str]] = Field(None, example={"key1": "value1", "key2": "value2"}, description="Additional metadata to be added to the resource package as extras.")
