from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict

class Resource(BaseModel):
    id: str = Field(..., 
                    json_schema_extra={
                        "description": "The unique identifier of the resource.",
                        "example": "65d337da-9069-4731-953f-0de4b2e8560d"})
    url: Optional[str] = Field(...,
                               json_schema_extra={
                                   "description": "The URL of the resource.",
                                   "example": "http://example.com/resource"})
    name: str = Field(...,
                      json_schema_extra={
                          "description": "The name of the resource.",
                          "example": "Example Resource Name"})
    description: Optional[str] = Field(None,
                                       json_schema_extra={
                                           "description": "A description of the resource.",
                                           "example": "This is an example resource."})
    format: Optional[str] = Field(None,
                                  json_schema_extra={
                                      "description": "The format of the resource.",
                                      "example": "CSV"})

class DataSourceResponse(BaseModel):
    id: str = Field(..., alias="id",
                    json_schema_extra={
                        "description": "The unique identifier of the dataset.",
                        "example": "4e2f5142-9490-436c-aefb-987142829b17"})
    name: str = Field(..., alias="name",
                      json_schema_extra={
                          "description": "The unique name of the dataset.",
                          "example": "example_dataset_name"})
    title: str = Field(..., alias="title", 
                       json_schema_extra={
                           "description": "The title of the dataset.",
                           "example": "Example Dataset Title"})
    organization_id: Optional[str] = Field(None, alias="owner_org",
                                           json_schema_extra={
                                               "description": "The ID of the organization that owns the dataset.",
                                               "example": "15559c52-9faa-4360-ad0c-3b0602da65f8"})
    description: Optional[str] = Field(None, alias="notes",
                                       json_schema_extra={"description": "A description of the dataset.",
                                                          "example": "This is an example dataset."})
    resources: List[Resource] = Field(...,
                                      json_schema_extra={
                                          "description": "A list of resources associated with the dataset."})
    extras: Optional[Dict[str, str]] = Field(None, 
                                             json_schema_extra={
                                                 "description": "Additional metadata associated with the dataset.",
                                                 "example": {"key1": "value1", "key2": "value2"}})

    model_config = ConfigDict(populate_by_name=True)
