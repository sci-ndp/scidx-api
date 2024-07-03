from fastapi import APIRouter, HTTPException, status, Depends
from api.services import default_services
from tenacity import RetryError
from typing import Dict, Any

from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.delete(
    "/dataset/{dataset_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Delete a dataset",
    description="Delete a dataset and its associated metadata from the system.",
    responses={
        200: {
            "description": "Dataset deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Dataset deleted successfully"}
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error deleting dataset: <error message>"}
                }
            }
        }
    }
)
async def delete_dataset_entry(
    dataset_id: str,
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a dataset and its associated metadata from the system.

    Parameters
    ----------
    dataset_id : str
        The ID of the dataset to be deleted.

    Returns
    -------
    dict
        A dictionary containing a success message if the dataset is deleted successfully.

    Raises
    ------
    HTTPException
        If there is an error deleting the dataset, an HTTPException is raised with a detailed message.
    """
    try:
        message = default_services.delete_dataset(dataset_id)
        return {"message": message}
    except RetryError as e:
        final_exception = e.last_attempt.exception()
        raise HTTPException(status_code=400, detail=str(final_exception))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
