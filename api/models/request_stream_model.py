from pydantic import BaseModel, Field
from typing import List, Optional

class ProducerPayload(BaseModel):
    keywords: Optional[str] = Field(
        None,
        description="Comma-separated keywords to target specific data streams.",
        json_schema_extra={"example": "temperature,bme280"},
    )
    match_all: bool = Field(
        False,
        description=(
            "Specifies whether all keywords must match (true) or if matching "
            "any one keyword (false) is sufficient."
        ),
        json_schema_extra={"example": False},
    )
    filter_semantics: List[str] = Field(
        [],
        description="List of abstraction strings for filtering data streams.",
        json_schema_extra={"example": ["temp>10", "humidity<=10"]},
    )
