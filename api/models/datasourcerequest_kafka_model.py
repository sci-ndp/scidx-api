from pydantic import BaseModel, Field

class KafkaDataSourceRequest(BaseModel):
    dataset_name: str = Field(..., json_schema_extra={"example": "kafka_topic_example", "description": "The unique name of the dataset to be created."})
    dataset_title: str = Field(..., json_schema_extra={"example": "Kafka Topic Example", "description": "The title of the dataset to be created."})
    owner_org: str = Field(..., json_schema_extra={"example": "organization_id", "description": "The ID of the organization to which the dataset belongs."})
    kafka_topic: str = Field(..., json_schema_extra={"example": "example_topic", "description": "The Kafka topic name."})
    kafka_host: str = Field(..., json_schema_extra={"example": "kafka_host", "description": "The Kafka host."})
    kafka_port: str = Field(..., json_schema_extra={"example": "kafka_port", "description": "The Kafka port."})
    dataset_description: str = Field("", json_schema_extra={"example": "This is an example Kafka topic registered as a system dataset.", "description": "A description of the dataset."})
