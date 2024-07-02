from pydantic import BaseModel, Field
from typing import Optional, Dict

class KafkaDataSourceRequest(BaseModel):
    dataset_name: str = Field(..., example="kafka_topic_example", description="The unique name of the dataset to be created.")
    dataset_title: str = Field(..., example="Kafka Topic Example", description="The title of the dataset to be created.")
    owner_org: str = Field(..., example="organization_id", description="The ID of the organization to which the dataset belongs.")
    kafka_topic: str = Field(..., example="example_topic", description="The Kafka topic name.")
    kafka_host: str = Field(..., example="kafka_host", description="The Kafka host.")
    kafka_port: str = Field(..., example="kafka_port", description="The Kafka port.")
    dataset_description: str = Field("", example="This is an example Kafka topic registered as a system dataset.", description="A description of the dataset.")
    extras: Optional[Dict[str, str]] = Field(None, example={"key1": "value1", "key2": "value2"}, description="Additional metadata to be added to the dataset as extras.")

