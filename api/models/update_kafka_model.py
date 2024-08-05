from typing import Dict, Optional
from pydantic import BaseModel, Field

class KafkaDataSourceUpdateRequest(BaseModel):
    dataset_name: Optional[str] = Field(None, example="kafka_topic_example", description="The unique name of the dataset.")
    dataset_title: Optional[str] = Field(None, example="Kafka Topic Example", description="The title of the dataset.")
    owner_org: Optional[str] = Field(None, example="organization_id", description="The ID of the organization to which the dataset belongs.")
    kafka_topic: Optional[str] = Field(None, example="example_topic", description="The Kafka topic name.")
    kafka_host: Optional[str] = Field(None, example="kafka_host", description="The Kafka host.")
    kafka_port: Optional[int] = Field(None, example=9092, description="The Kafka port.")
    dataset_description: Optional[str] = Field(None, example="This is an example Kafka topic registered as a system dataset.", description="A description of the dataset.")
    extras: Optional[Dict[str, str]] = Field(None, example={"key1": "value1", "key2": "value2"}, description="Additional metadata to be added or updated for the dataset.")
    mapping: Optional[Dict[str, str]] = Field(None, example={"field1": "mapping1", "field2": "mapping2"}, description="Mapping information for the dataset.")
    processing: Optional[Dict[str, str]] = Field(None, example={"data_key": "data", "info_key": "info"}, description="Processing information for the dataset.")
