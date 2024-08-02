import json
from typing import List, Optional
from ckanapi import NotFound
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from api.config.ckan_settings import ckan_settings
from api.models import DataSourceResponse, Resource
from api.services.default_services import log_retry_attempt

@retry(
    wait=wait_exponential(multiplier=1, max=2),
    stop=stop_after_attempt(5),
    retry=retry_if_exception_type(Exception),
    after=log_retry_attempt
)
async def search_datasource(
    dataset_name: Optional[str] = None,
    dataset_title: Optional[str] = None,
    owner_org: Optional[str] = None,
    resource_url: Optional[str] = None,
    resource_name: Optional[str] = None,
    dataset_description: Optional[str] = None,
    resource_description: Optional[str] = None,
    resource_format: Optional[str] = None,
    search_term: Optional[str] = None,
    server: Optional[str] = "local"
) -> List[DataSourceResponse]:
    if server not in ["local", "global"]:
        raise Exception("Invalid server specified. Please specify 'local' or 'global'")

    if server == "local":
        ckan = ckan_settings.ckan_no_api_key  # Use the no API key instance
    elif server == "global":
        ckan = ckan_settings.ckan_global

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
            # Convert the dataset to a string representation
            dataset_str = json.dumps(dataset, default=str).lower()

            # Check if all search params are present in the dataset string
            if all(param.lower() in dataset_str for param in search_params):
                include_dataset = False
                if resource_url or resource_name or resource_description or resource_format:
                    resources = dataset.get('resources', [])
                    for resource in resources:
                        if (
                            (resource_url and resource.get('url') == resource_url) or
                            (resource_name and resource.get('name') == resource_name) or
                            (resource_description and resource.get('description') == resource_description) or
                            (resource_format and resource.get('format').lower() == resource_format)
                        ):
                            include_dataset = True
                            break
                else:
                    include_dataset = True

                if include_dataset:
                    resources_list = [
                        Resource(
                            id=res['id'],
                            url=res['url'],
                            name=res['name'],
                            description=res.get('description'),
                            format=res.get('format')
                        ) for res in dataset.get('resources', [])
                    ]

                    organization_name = dataset.get('organization', {}).get('name') if dataset.get('organization') else None

                    extras = {extra['key']: extra['value'] for extra in dataset.get('extras', [])}

                    # Convert mapping and processing fields back to JSON
                    if 'mapping' in extras:
                        extras['mapping'] = json.loads(extras['mapping'])
                    if 'processing' in extras:
                        extras['processing'] = json.loads(extras['processing'])

                    results.append(DataSourceResponse(
                        id=dataset['id'],
                        name=dataset['name'],
                        title=dataset['title'],
                        owner_org=organization_name,
                        description=dataset.get('notes'),
                        resources=resources_list,
                        extras=extras
                    ))

        return results

    except NotFound:
        return []
    except Exception as e:
        raise Exception(f"Error searching for datasets: {str(e)}")
