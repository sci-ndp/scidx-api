from fastapi import APIRouter, HTTPException, status, Depends, Body
from api.services.streaming_services.stream_manager import create_stream
from api.models.request_stream_model import ProducerPayload
from typing import Dict, Any
from api.services.keycloak_services.get_current_user import get_current_user

router = APIRouter()

@router.post(
    "/stream",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Kafka stream",
    description=(
        "Create a new Kafka stream with the filtered and standardized data.\n\n"
        "### Common Fields for Creating a Stream\n"
        "- **keywords**: Keywords to search for relevant streams.\n"
        "- **match_all**: Boolean to indicate whether all keywords must match (`true`) or any of them (`false`).\n"
        "- **filter_semantics**: The filtering conditions for the stream data. This can include simple conditions, mathematical operations, "
        "IF-THEN conditions, or window-based filtering.\n\n"
        "### Filter Types and Examples\n\n"
        "1. **Simple Condition Filters (Operands for Numeric and String Fields)**\n"
        "    - Numeric fields support `>`, `<`, `>=`, `<=`, `=`, `!=`, and `IN`.\n"
        "    - String fields support `=`, `!=`, and `IN`.\n\n"
        "    ```json\n"
        '    "filter_semantics": [\n'
        '        "temperature > 20",\n'
        '        "humidity <= 50",\n'
        '        "status = \'active\'",\n'
        '        "country IN [\'US\', \'Canada\']"\n'
        "    ]\n"
        "    ```\n"
        "2. **Mathematical Operations**\n"
        "    - Use `+`, `-`, `*`, and `/` to perform calculations before applying comparisons.\n\n"
        "    ```json\n"
        '    "filter_semantics": [\n'
        '        "(speed * time) > 100",\n'
        '        "(price + tax) < 1000"\n'
        "    ]\n"
        "    ```\n"
        "3. **IF-THEN Filters**\n"
        "    - Apply conditional logic to determine the value of a field based on another field.\n\n"
        "    ```json\n"
        '    "filter_semantics": [\n'
        '        "IF temperature > 25 THEN warning = \'high_temp\'",\n'
        '        "IF status = \'active\' THEN priority = \'high\'"\n'
        "    ]\n"
        "    ```\n"
        "4. **IF-THEN-ELSE Filters**\n"
        "    - Similar to IF-THEN, but also defines an `ELSE` condition.\n\n"
        "    ```json\n"
        '    "filter_semantics": [\n'
        '        "IF temperature > 25 THEN warning = \'high_temp\' ELSE warning = \'normal\'",\n'
        '        "IF score >= 90 THEN grade = \'A\' ELSE grade = \'B\'"\n'
        "    ]\n"
        "    ```\n"
        "5. **Column-to-Column Comparisons**\n"
        "    - Compare two columns and apply the result to another field.\n\n"
        "    ```json\n"
        '    "filter_semantics": [\n'
        '        "IF temperature > humidity THEN alert = \'temp_high\'",\n'
        '        "IF salary >= bonus THEN status = \'eligible\'"\n'
        "    ]\n"
        "    ```\n"
        "6. **Complex Conditions Using AND/OR**\n"
        "    - Combine multiple conditions with `AND` or `OR`.\n\n"
        "    ```json\n"
        '    "filter_semantics": [\n'
        '        "temperature > 20 AND humidity < 30",\n'
        '        "pressure > 1000 OR wind_speed > 5"\n'
        "    ]\n"
        "    ```\n"
        "7. **Window Filter**\n"
        "    - Apply a statistic (like `mean`, `sum`, etc.) over a sliding window of data points, then apply a filter condition to the result.\n"
        "    - **Parameters:**\n"
        "      1. **window size**: The number of data points in the window.\n"
        "      2. **statistic**: The statistical operation to perform over the window (e.g., `mean`, `sum`, etc.).\n"
        "      3. **condition**: The condition to apply to the windowed data.\n\n"
        "    ```json\n"
        '    "filter_semantics": [\n'
        '        "window_filter(10, mean, \'temperature > 30\')"\n'
        "    ]\n"
        "    ```\n"
        "8. **Window Filter with IF-THEN Logic**\n"
        "    - Combine window-based filtering with IF-THEN logic.\n\n"
        "    ```json\n"
        '    "filter_semantics": [\n'
        '        "window_filter(10, mean, \'IF temperature > 30 THEN alert = red\')"\n'
        "    ]\n"
        "    ```\n"
        "9. **Window Filter with IF-THEN-ELSE Logic**\n"
        "    - Combine window-based filtering with both IF-THEN and ELSE logic.\n\n"
        "    ```json\n"
        '    "filter_semantics": [\n'
        '        "window_filter(10, mean, \'IF temperature > 30 THEN alert = red ELSE alert = blue\')"\n'
        "    ]\n"
        "    ```\n"
    ),
    responses={
        201: {
            "description": "Stream created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "topic": "data_stream_1234",
                        "involved_streams": ["stream_id_1", "stream_id_2"]
                    }
                }
            }
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Error creating stream: <error message>"
                    }
                }
            }
        }
    }
)
async def create_kafka_stream(
    payload: ProducerPayload = Body(...),
    _: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a Kafka stream with the specified filtering semantics and 
    keywords.

    Parameters
    ----------
    payload : ProducerPayload
        The payload containing all filtering and windowing options.

    Returns
    -------
    dict
        A dictionary containing the stream topic and the involved streams.

    Raises
    ------
    HTTPException
        If there is an error creating the stream, an HTTPException is raised.
    """
    try:
        data_stream_id, involved_stream_ids = await create_stream(payload)
        return {
            "topic": f"data_stream_{data_stream_id}",
            "involved_streams": involved_stream_ids
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
