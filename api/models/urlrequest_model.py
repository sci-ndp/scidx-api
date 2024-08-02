from pydantic import BaseModel, Field, root_validator, ValidationError
from typing import Dict, Optional, Union, Any
from enum import Enum

# Define an enumeration for file types
class FileTypeEnum(str, Enum):
    stream = "stream"
    CSV = "CSV"
    TXT = "TXT"
    JSON = "JSON"
    NetCDF = "NetCDF"

# Define processing info models for each file type
class StreamProcessingInfo(BaseModel):
    refresh_rate: Optional[str] = Field(None, example="5 seconds", description="The refresh rate for the data stream.")
    data_key: Optional[str] = Field(None, example="results", description="The key for the response data in the JSON file.")

class CSVProcessingInfo(BaseModel):
    delimiter: str = Field(..., example=",", description="The delimiter used in the CSV file.")
    header_line: int = Field(..., example=1, description="The line number of the header in the CSV file.")
    start_line: int = Field(..., example=2, description="The line number where the data starts in the CSV file.")
    comment_char: Optional[str] = Field(None, example="#", description="The character used for comments in the CSV file.")

class TXTProcessingInfo(BaseModel):
    delimiter: str = Field(..., example="\t", description="The delimiter used in the TXT file.")
    header_line: int = Field(..., example=1, description="The line number of the header in the TXT file.")
    start_line: int = Field(..., example=2, description="The line number where the data starts in the TXT file.")

class JSONProcessingInfo(BaseModel):
    info_key: Optional[str] = Field(None, example="count", description="The key for additional information in the JSON file.")
    additional_key: Optional[str] = Field(None, example="", description="An additional key in the JSON file.")
    data_key: Optional[str] = Field(None, example="results", description="The key for the response data in the JSON file.")

class NetCDFProcessingInfo(BaseModel):
    group: Optional[str] = Field(None, example="group_name", description="The group within the NetCDF file.")

# Define the main request model
class URLRequest(BaseModel):
    resource_name: str = Field(..., example="example_resource_name", description="The unique name of the resource to be created.")
    resource_title: str = Field(..., example="Example Resource Title", description="The title of the resource to be created.")
    owner_org: str = Field(..., example="example_org_id", description="The ID of the organization to which the resource belongs.")
    resource_url: str = Field(..., example="http://example.com/resource", description="The URL of the resource to be added.")
    file_type: Optional[FileTypeEnum] = Field(..., example="CSV", description="The type of the file (e.g., stream, CSV, TXT, JSON, NetCDF).")
    notes: str = Field("", example="Additional notes about the resource.", description="Additional notes about the resource.")
    extras: Optional[Dict[str, str]] = Field(None, example={"key1": "value1", "key2": "value2"}, description="Additional metadata to be added to the resource package as extras.")
    mapping: Optional[Dict[str, str]] = Field(None, example={"field1": "mapping1", "field2": "mapping2"}, description="Mapping information for the dataset.")
    processing: Optional[Dict[str, Any]] = Field(None, example={"data_key": "data", "info_key": "info"}, description="Processing information for the dataset.")

    @root_validator(pre=True)
    def check_processing(cls, values):
        file_type = values.get('file_type')
        processing = values.get('processing')

        if file_type == "stream":
            try:
                StreamProcessingInfo(**processing)
            except ValidationError as e:
                raise ValueError(f"Invalid processing info for file_type 'stream': {e}")
        elif file_type == "CSV":
            try:
                CSVProcessingInfo(**processing)
            except ValidationError as e:
                raise ValueError(f"Invalid processing info for file_type 'CSV': {e}")
        elif file_type == "TXT":
            try:
                TXTProcessingInfo(**processing)
            except ValidationError as e:
                raise ValueError(f"Invalid processing info for file_type 'TXT': {e}")
        elif file_type == "JSON":
            try:
                JSONProcessingInfo(**processing)
            except ValidationError as e:
                raise ValueError(f"Invalid processing info for file_type 'JSON': {e}")
        elif file_type == "NetCDF":
            try:
                NetCDFProcessingInfo(**processing)
            except ValidationError as e:
                raise ValueError(f"Invalid processing info for file_type 'NetCDF': {e}")
        else:
            raise ValueError(f"Unsupported file_type: {file_type}")

        return values
