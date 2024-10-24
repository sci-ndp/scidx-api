from fastapi import APIRouter, HTTPException
from api.services.streaming_services.producer import delete_specific_stream

router = APIRouter()

@router.delete(
    "/stream/{stream_id_or_name}",
    response_model=dict,
    summary="Delete a Kafka stream",
    description="Delete a Kafka stream by its ID (e.g., '1') or full topic name (e.g., 'data_stream_1').",
    responses={
        200: {
            "description": "Stream deleted successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Stream deleted successfully"}
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
                    "example": {"detail": "Stream not found"}
                }
            }
        }
    }
)
async def delete_stream(stream_id_or_name: str):
    """
    Endpoint to delete a Kafka stream by its ID (e.g., '1') or full topic name (e.g., 'data_stream_1').

    Parameters
    ----------
    stream_id_or_name : str
        The stream ID or full topic name to delete.

    Returns
    -------
    dict
        A message confirming the deletion of the stream.

    Raises
    ------
    HTTPException
        If there is an error deleting the stream, an HTTPException is raised with a detailed message.
    """
    try:
        await delete_specific_stream(stream_id_or_name)
        return {"message": f"Stream '{stream_id_or_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
