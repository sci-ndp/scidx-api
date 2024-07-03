from pydantic import BaseModel, Field
from typing import Optional, Dict

class URLRequest(BaseModel):
    resource_name: str = Field(..., example="example_resource_name", description="The unique name of the resource to be created.")
    resource_title: str = Field(..., example="Example Resource Title", description="The title of the resource to be created.")
    owner_org: str = Field(..., example="example_org_id", description="The ID of the organization to which the resource belongs.")
    resource_url: str = Field(..., example="http://example.com/resource", description="The URL of the resource to be added.")
    notes: str = Field("", example="Additional notes about the resource.", description="Additional notes about the resource.")
    extras: Optional[Dict[str, str]] = Field(None, example={"key1": "value1", "key2": "value2"}, description="Additional metadata to be added to the resource package as extras.")

class URLUpdateRequest(BaseModel):
    resource_name: Optional[str] = Field(None, example="example_resource_name", description="The unique name of the resource to be created.")
    resource_title: Optional[str] = Field(None, example="Example Resource Title", description="The title of the resource to be created.")
    owner_org: Optional[str] = Field(None, example="example_org_id", description="The ID of the organization to which the resource belongs.")
    resource_url: Optional[str] = Field(None, example="http://example.com/resource", description="The URL of the resource to be added.")
    notes: Optional[str] = Field(None, example="Additional notes about the resource.", description="Additional notes about the resource.")
    extras: Optional[Dict[str, str]] = Field(None, example={"key1": "value1", "key2": "value2"}, description="Additional metadata to be added to the resource package as extras.")
