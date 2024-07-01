from pydantic import BaseModel, Field
from typing import Optional, Dict

class DataSourceRequest(BaseModel):
    dataset_name: str = Field(..., example="example_dataset_name", description="The unique name of the dataset to be created.")
    dataset_title: str = Field(..., example="Example Dataset Title", description="The title of the dataset to be created.")
    owner_org: str = Field(..., example="example_org_id", description="The ID of the organization to which the dataset belongs.")
    resource_url: str = Field(..., example="http://example.com/resource", description="The URL of the resource to be associated with the dataset.")
    resource_name: str = Field(..., example="Example Resource Name", description="The name of the resource to be associated with the dataset.")
    dataset_description: str = Field("", example="This is an example dataset.", description="A description of the dataset.")
    resource_description: str = Field("", example="This is an example resource.", description="A description of the resource.")
    resource_format: str = Field(None, example="CSV", description="The format of the resource.")
    extras: Optional[Dict[str, str]] = Field(None, example={"key1": "value1", "key2": "value2"}, description="Additional metadata to be added to the dataset as extras.")
