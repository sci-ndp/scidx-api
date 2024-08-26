from pydantic import BaseModel, Field
from typing import Dict, Optional

class KafkaDataSourceRequest(BaseModel):
    dataset_name: str = Field(
        ...,
        description="The unique name of the dataset to be created.",
        json_schema_extra={"example": "kafka_topic_example"},
    )
    dataset_title: str = Field(
        ...,
        description="The title of the dataset to be created.",
        json_schema_extra={"example": "Kafka Topic Example"},
    )
    owner_org: str = Field(
        ...,
        description="The ID of the organization to which the dataset belongs.",
        json_schema_extra={"example": "organization_id"},
    )
    kafka_topic: str = Field(
        ...,
        description="The Kafka topic name.",
        json_schema_extra={"example": "example_topic"},
    )
    kafka_host: str = Field(
        ...,
        description="The Kafka host.",
        json_schema_extra={"example": "kafka_host"},
    )
    kafka_port: str = Field(
        ...,
        description="The Kafka port.",
        json_schema_extra={"example": "kafka_port"},
    )
    dataset_description: str = Field(
        "",
        description="A description of the dataset.",
        json_schema_extra={
            "example": "This is an example Kafka topic registered as a system dataset.",
        },
    )
    extras: Optional[Dict[str, str]] = Field(
        None,
        description="Additional metadata to be added to the dataset as extras.",
        json_schema_extra={"example": {"key1": "value1", "key2": "value2"}},
    )
    mapping: Optional[Dict[str, str]] = Field(
        None,
        description=(
            "Mapping information for the dataset. "
            "For selecting the desired fields to send and how they will be named."
        ),
        json_schema_extra={"example": {"field1": "mapping1", "field2": "mapping2"}},
    )
    processing: Optional[Dict[str, str]] = Field(
        None,
        description="Processing information for the dataset.",
        json_schema_extra={"example": {"data_key": "data", "info_key": "info"}},
    )
