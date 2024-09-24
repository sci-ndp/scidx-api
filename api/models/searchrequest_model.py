from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    dataset_name: str = Field(
        None, 
        description="The name of the dataset.",
    )
    dataset_title: str = Field(
        None, 
        description="The title of the dataset.",
    )
    owner_org: str = Field(
        None, 
        description="The name of the organization.",
    )
    resource_url: str = Field(
        None, 
        description="The URL of the dataset resource.",
    )
    resource_name: str = Field(
        None, 
        description="The name of the dataset resource.",
    )
    dataset_description: str = Field(
        None, 
        description="The description of the dataset.",
    )
    resource_description: str = Field(
        None, 
        description="The description of the dataset resource.",
    )
    resource_format: str = Field(
        None, 
        description="The format of the dataset resource.",
    )
    search_term: str = Field(
        None, 
        description="A term to search across all fields.",
    )
    filter_list: list[str] = Field(
        None,
        description="A list of field filters"
    )
    timestamp: str = Field(
        None, 
        description="A time range term to filter results.",
    )
    server: Optional[Literal['local', 'global']] = Field(
        'local', description="Specify the server to search on: 'local' or 'global'."
    )
