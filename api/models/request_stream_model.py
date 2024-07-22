from pydantic import BaseModel, Field
from typing import List, Optional

class ProducerPayload(BaseModel):
    keywords: Optional[str] = Field(None, example="temperature,bme280", description="Comma-separated keywords to target specific data streams.")
    match_all: bool = Field(True, example=True, description="Specifies whether all keywords must match (true) or if matching any one keyword (false) is sufficient.")
    filter_semantics: List[str] = Field([], example=["temp>10", "humidity<=10"], description="List of abstraction strings for filtering data streams.")
