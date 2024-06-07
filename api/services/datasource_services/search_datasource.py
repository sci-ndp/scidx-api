from typing import List, Optional
from ckanapi import NotFound
from api.config.ckan_settings import ckan_settings
from api.models import DataSourceResponse, Resource

def search_datasource(
    dataset_name: Optional[str] = None,
    dataset_title: Optional[str] = None,
    organization_id: Optional[str] = None,
    owner_org: Optional[str] = None,
    resource_url: Optional[str] = None,
    resource_name: Optional[str] = None,
    dataset_description: Optional[str] = None,
    resource_description: Optional[str] = None,
    resource_format: Optional[str] = None,
    search_term: Optional[str] = None  # New parameter for global search
) -> List[DataSourceResponse]:
    """
    Search for datasets based on various parameters.

    Parameters
    ----------
    dataset_name : Optional[str]
        The name of the dataset.
    dataset_title : Optional[str]
        The title of the dataset.
    organization_id : Optional[str]
        The ID of the organization that owns the dataset.
    owner_org: Optional[str]
        The name of the organization that owns the dataset.
    resource_url : Optional[str]
        The URL of the dataset resource.
    resource_name : Optional[str]
        The name of the dataset resource.
    dataset_description : Optional[str]
        The description of the dataset.
    resource_description : Optional[str]
        The description of the dataset resource.
    resource_format : Optional[str]
        The format of the dataset resource.
    search_term : Optional[str]
        A word or fragment of a word to search in any field of the dataset.

    Returns
    -------
    List[DataSourceResponse]
        A list of datasets that match the search criteria.

    Raises
    ------
    Exception
        If there is an error during the search.
    """
    ckan = ckan_settings.ckan
    search_params = []

    # Add search parameters based on provided arguments
    if dataset_name:
        search_params.append(f'name:{dataset_name}')
    if dataset_title:
        search_params.append(f'title:{dataset_title}')
    if organization_id:
        search_params.append(f'owner_org:{organization_id}')
    if dataset_description:
        search_params.append(f'notes:{dataset_description}')
    if search_term:
        search_params.append(search_term)  # Add search term for global search

    # Create the query string for the CKAN search
    query_string = " AND ".join(search_params) if search_params else "*:*"

    try:
        # Perform the search using CKAN's package_search action
        datasets = ckan.action.package_search(q=query_string, rows=1000)  # Adjust rows as needed

        results = []

        # Process each dataset in the search results
        for dataset in datasets['results']:
            # Filter by owner_org (organization name) if specified
            organization_name = dataset.get('organization', {}).get('name')
            if owner_org and organization_name != owner_org:
                continue

            # Determine if the dataset should be included based on resource filters
            include_dataset = False
            if resource_url or resource_name or resource_description or resource_format:
                resources = dataset.get('resources', [])
                for resource in resources:
                    if (
                        (resource_url and resource.get('url') == resource_url) or
                        (resource_name and resource.get('name') == resource_name) or
                        (resource_description and resource.get('description') == resource_description) or
                        (resource_format and resource.get('format') == resource_format)
                    ):
                        include_dataset = True
                        break
            else:
                include_dataset = True

            if include_dataset:
                # Create a list of Resource objects from the dataset's resources
                resources_list = [
                    Resource(
                        id=res['id'],
                        url=res['url'],
                        name=res['name'],
                        description=res.get('description'),
                        format=res.get('format')
                    ) for res in dataset.get('resources', [])
                ]

                # Append the DataSourceResponse object to the results list
                results.append(DataSourceResponse(
                    id=dataset['id'],
                    name=dataset['name'],
                    title=dataset['title'],
                    owner_org=organization_name,  # Use organization_name for the owner_org field
                    description=dataset.get('notes'),
                    resources=resources_list
                ))
        
        return results

    except NotFound:
        return []
    except Exception as e:
        raise Exception(f"Error searching for datasets: {str(e)}")
