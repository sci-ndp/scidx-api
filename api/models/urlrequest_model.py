from pydantic import BaseModel, Field
from typing import Dict, Optional

class URLRequest(BaseModel):
    resource_name: str = Field(..., example="example_resource_name", description="The unique name of the resource to be created.")
    resource_title: str = Field(..., example="Example Resource Title", description="The title of the resource to be created.")
    owner_org: str = Field(..., example="example_org_id", description="The ID of the organization to which the resource belongs.")
    resource_url: str = Field(..., example="http://example.com/resource", description="The URL of the resource to be added.")
    file_type: str = Field(..., example="CSV", description="The type of the file (e.g., stream, CSV, TXT, JSON, NetCDF).")
    notes: str = Field("", example="Additional notes about the resource.", description="Additional notes about the resource.")
    extras: Optional[Dict[str, str]] = Field(None, example={"key1": "value1", "key2": "value2"}, description="Additional metadata to be added to the resource package as extras.")
    mapping: Optional[Dict[str, str]] = Field(None, example={"field1": "mapping1", "field2": "mapping2"}, description="Mapping information for the dataset.")
    processing: Optional[Dict[str, str]] = Field(None, example={"data_key": "data", "info_key": "info"}, description="Processing information for the dataset.")

