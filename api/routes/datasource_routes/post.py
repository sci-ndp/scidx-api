from fastapi import APIRouter, HTTPException, status

from api.services import datasource_services
from api.models import DataSourceRequest

router = APIRouter()


@router.post(
    "/",
    response_model=str,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new data source",
    description="Create a new dataset and its associated resource in CKAN.",
    responses={
        201: {
            "description": "Dataset created successfully",
            "content": {
                "application/json": {
                    "example": "12345678-abcd-efgh-ijkl-1234567890ab"
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error creating dataset: <error message>"}
                }
            }
        }
    }
)
async def create_datasource(data: DataSourceRequest):
    """
    Add a dataset and its associated resource to CKAN.

    Parameters
    ----------
    data : DataSourceRequest
        An object containing all the required parameters for creating a dataset and resource.

    Returns
    -------
    str
        The ID of the created dataset if successful.

    Raises
    ------
    HTTPException
        If there is an error creating the dataset or resource, an HTTPException is raised with a detailed message.
    """
    try:
        dataset_id = datasource_services.add_datasource(
            dataset_name=data.dataset_name,
            dataset_title=data.dataset_title,
            organization_id=data.organization_id,
            resource_url=data.resource_url,
            resource_name=data.resource_name,
            dataset_description=data.dataset_description,
            resource_description=data.resource_description,
            resource_format=data.resource_format
        )
        return dataset_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
