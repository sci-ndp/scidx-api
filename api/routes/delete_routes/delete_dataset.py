from fastapi import APIRouter, HTTPException, Query
from api.services import dataset_services
from typing import Annotated

router = APIRouter()

@router.delete(
    "/resource",
    response_model=dict,
    summary="Delete a resource by id",
    description="Delete a resource by its id.",
    responses={
        200: {
            "description": "Resource deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Resource deleted successfully"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error message explaining the bad request"
                    }
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Resource not found"}
                }
            }
        }
    }
)
async def delete_resource(
    resource_id: Annotated[str, Query(description="The ID of the dataset to delete.")]
    ):
    """
    Endpoint to delete a resource by its type and name.

    Parameters
    ----------
    resource_id : str
        The id of the resource to be deleted.

    Returns
    -------
    dict
        A message confirming the deletion of the resource.

    Raises
    ------
    HTTPException
        If there is an error deleting the resource, an HTTPException is 
        raised with a detailed message.
    """
    try:
        dataset_services.delete_dataset(resource_id=resource_id)
        return {"message": f"{resource_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete(
    "/resource/{resource_name}",
    response_model=dict,
    summary="Delete a resource",
    description="Delete a resource by its type and name.",
    responses={
        200: {
            "description": "Resource deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Resource deleted successfully"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error message explaining the bad request"
                    }
                }
            }
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "Resource not found"}
                }
            }
        }
    }
)
async def delete_resource(resource_name: str):
    """
    Endpoint to delete a resource by its type and name.

    Parameters
    ----------
    resource_name : str
        The name of the resource to be deleted.

    Returns
    -------
    dict
        A message confirming the deletion of the resource.

    Raises
    ------
    HTTPException
        If there is an error deleting the resource, an HTTPException is 
        raised with a detailed message.
    """
    try:
        dataset_services.delete_dataset(dataset_name=resource_name)
        return {"message": f"{resource_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
