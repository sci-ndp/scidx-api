from pydantic import BaseModel, Field
from typing import List, Optional

class Resource(BaseModel):
    id: str
    url: str
    name: str
    description: Optional[str] = None
    format: Optional[str] = None

class DataSourceResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")
    title: str = Field(..., alias="title")
    organization_id: Optional[str] = Field(None, alias="owner_org")
    description: Optional[str] = Field(None, alias="notes")
    resources: List[Resource] = []

    class Config:
        allow_population_by_field_name = True
