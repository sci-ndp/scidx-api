from typing import Dict, Optional
from pydantic import BaseModel, Field

class KafkaDataSourceUpdateRequest(BaseModel):
    dataset_name: Optional[str] = Field(
        None,
        description="The unique name of the dataset.",
        json_schema_extra={"example": "kafka_topic_example"},
    )
    dataset_title: Optional[str] = Field(
        None,
        description="The title of the dataset.",
        json_schema_extra={"example": "Kafka Topic Example"},
    )
    owner_org: Optional[str] = Field(
        None,
        description="The ID of the organization to which the dataset belongs.",
        json_schema_extra={"example": "organization_id"},
    )
    kafka_topic: Optional[str] = Field(
        None,
        description="The Kafka topic name.",
        json_schema_extra={"example": "example_topic"},
    )
    kafka_host: Optional[str] = Field(
        None,
        description="The Kafka host.",
        json_schema_extra={"example": "kafka_host"},
    )
    kafka_port: Optional[int] = Field(
        None,
        description="The Kafka port.",
        json_schema_extra={"example": 9092},
    )
    dataset_description: Optional[str] = Field(
        None,
        description="A description of the dataset.",
        json_schema_extra={
            "example": "This is an example Kafka topic registered as a system dataset."
        },
    )
    extras: Optional[Dict[str, str]] = Field(
        None,
        description="Additional metadata to be added or updated for the dataset.",
        json_schema_extra={"example": {"key1": "value1", "key2": "value2"}},
    )
    mapping: Optional[Dict[str, str]] = Field(
        None,
        description="Mapping information for the dataset.",
        json_schema_extra={"example": {"field1": "mapping1", "field2": "mapping2"}},
    )
    processing: Optional[Dict[str, str]] = Field(
        None,
        description="Processing information for the dataset.",
        json_schema_extra={"example": {"data_key": "data", "info_key": "info"}},
    )
