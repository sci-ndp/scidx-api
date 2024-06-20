from typing import List, Optional
from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings
from api.models.response_kafka_model import KafkaDataSourceResponse, KafkaResource

def search_kafka(
    dataset_name: Optional[str] = None,
    dataset_title: Optional[str] = None,
    owner_org: Optional[str] = None,
    kafka_host: Optional[str] = None,
    kafka_port: Optional[str] = None,
    kafka_topic: Optional[str] = None,
    dataset_description: Optional[str] = None,
    search_term: Optional[str] = None  # Add search_term parameter
) -> List[KafkaDataSourceResponse]:
    """
    Search for Kafka datasets based on various parameters.

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
    Exception
        If there is an error during the search.
    """
    ckan = ckan_settings.ckan
    search_params = []

    if search_term:
        search_params.append(search_term)
    else:
        if dataset_name:
            search_params.append(f'name:{dataset_name}')
        if dataset_title:
            search_params.append(f'title:{dataset_title}')
        if owner_org:
            search_params.append(f'organization:{owner_org}')
        if dataset_description:
            search_params.append(f'notes:{dataset_description}')

    query_string = " AND ".join(search_params) if search_params else "*:*"

    try:
        datasets = ckan.action.package_search(q=query_string, rows=1000)  # Adjust rows as needed

        results = []

        for dataset in datasets['results']:
            try:
                resources = dataset.get('resources', [])
                kafka_resources = [
                    KafkaResource(
                        id=res['id'],
                        kafka_host=res['url'].split(';')[0].replace('http://', ''),
                        kafka_port=res['url'].split(';')[1],
                        kafka_topic=res['url'].split(';')[2],
                        description=res.get('description')
                    )
                    for res in resources if res.get('format') == 'Kafka'
                ]

                if kafka_resources:
                    organization_name = dataset.get('organization', {}).get('name') if dataset.get('organization') else None

                    results.append(KafkaDataSourceResponse(
                        id=dataset['id'],
                        name=dataset['name'],
                        title=dataset['title'],
                        owner_org=organization_name,
                        description=dataset.get('notes'),
                        resources=kafka_resources
                    ))
            except IndexError:
                print(f"Skipping dataset {dataset['name']} due to index error in resources.")
            except Exception as e:
                print(f"Skipping dataset {dataset['name']} due to error: {str(e)}")

        return results

    except NotFound:
        return []
    except Exception as e:
        raise Exception(f"Error searching for Kafka datasets: {str(e)}")
