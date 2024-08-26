from pydantic import BaseModel, Field
from typing import Union

# Models for user authentication
class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="The access token provided after successful authentication.",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
    )
    token_type: str = Field(
        ...,
        description="The type of token provided.",
        json_schema_extra={"example": "bearer"},
    )

class TokenData(BaseModel):
    username: Union[str, None] = Field(
        None,
        description="The username associated with the token.",
        json_schema_extra={"example": "user123"},
    )
