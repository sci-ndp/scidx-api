from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from api.services.kafka_services.search_kafka import search_kafka
from api.models.response_kafka_model import KafkaDataSourceResponse

router = APIRouter()

@router.get(
    "/kafka",
    response_model=List[KafkaDataSourceResponse],
    summary="Search Kafka data sources",
    description="Search Kafka datasets by various parameters.",
    responses={
        200: {
            "description": "Kafka datasets retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "12345678-abcd-efgh-ijkl-1234567890ab",
                            "name": "example_kafka_topic",
                            "title": "Example Kafka Topic",
                            "owner_org": "example_org_name",
                            "description": "This is an example Kafka topic.",
                            "resources": [
                                {
                                    "id": "abcd1234-efgh5678-ijkl9012-mnop3456",
                                    "kafka_host": "kafka_host",
                                    "kafka_port": "kafka_port",
                                    "kafka_topic": "example_topic",
                                    "description": "This is an example Kafka resource."
                                }
                            ],
                            "extras": {
                                "key1": "value1",
                                "key2": "value2"
                            }
                        }
                    ]
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error message explaining the bad request"}
                }
            }
        }
    }
)
async def search_kafka_datasource(
    dataset_name: Optional[str] = Query(None, description="The name of the Kafka dataset."),
    dataset_title: Optional[str] = Query(None, description="The title of the Kafka dataset."),
    owner_org: Optional[str] = Query(None, description="The name of the organization."),
    kafka_host: Optional[str] = Query(None, description="The Kafka host."),
    kafka_port: Optional[str] = Query(None, description="The Kafka port."),
    kafka_topic: Optional[str] = Query(None, description="The Kafka topic."),
    dataset_description: Optional[str] = Query(None, description="The description of the Kafka dataset."),
    search_term: Optional[str] = Query(None, description="A term to search across all fields.")
):
    """
    Endpoint to search Kafka datasets in CKAN by various parameters.

    Parameters
    ----------
    dataset_name : Optional[str]
        The name of the Kafka dataset.
    dataset_title : Optional[str]
        The title of the Kafka dataset.
    owner_org : Optional[str]
        The name of the organization.
    kafka_host : Optional[str]
        The Kafka host.
    kafka_port : Optional[str]
        The Kafka port.
    kafka_topic : Optional[str]
        The Kafka topic.
    dataset_description : Optional[str]
        The description of the Kafka dataset.
    search_term : Optional[str]
        A term to search across all fields.

    Returns
    -------
    List[KafkaDataSourceResponse]
        A list of Kafka datasets that match the search criteria.

    Raises
    ------
    HTTPException
        If there is an error searching for the datasets, an HTTPException is raised with a detailed message.
    """
    try:
        results = search_kafka(
            dataset_name=dataset_name,
            dataset_title=dataset_title,
            owner_org=owner_org,
            kafka_host=kafka_host,
            kafka_port=kafka_port,
            kafka_topic=kafka_topic,
            dataset_description=dataset_description,
            search_term=search_term
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
