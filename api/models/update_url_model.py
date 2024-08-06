from pydantic import BaseModel, Field, root_validator, ValidationError
from typing import Dict, Optional, Any
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
class URLUpdateRequest(BaseModel):
    resource_name: Optional[str] = Field(None, example="example_resource_name", description="The unique name of the resource to be created.")
    resource_title: Optional[str] = Field(None, example="Example Resource Title", description="The title of the resource to be created.")
    owner_org: Optional[str] = Field(None, example="example_org_id", description="The ID of the organization to which the resource belongs.")
    resource_url: Optional[str] = Field(None, example="http://example.com/resource", description="The URL of the resource to be added.")
    file_type: Optional[FileTypeEnum] = Field(None, example="CSV", description="The type of the file (e.g., stream, CSV, TXT, JSON, NetCDF).")
    notes: Optional[str] = Field(None, example="Additional notes about the resource.", description="Additional notes about the resource.")
    extras: Optional[Dict[str, str]] = Field(None, example={"key1": "value1", "key2": "value2"}, description="Additional metadata to be added to the resource package as extras.")
    mapping: Optional[Dict[str, str]] = Field(None, example={"field1": "mapping1", "field2": "mapping2"}, description="Mapping information for the dataset.")
    processing: Optional[Dict[str, Any]] = Field(None, example={"data_key": "data", "info_key": "info"}, description="Processing information for the dataset.")

    # @root_validator(pre=True)
    # def check_processing(cls, values):
    #     file_type = values.get('file_type')
    #     processing = values.get('processing')

    #     if processing:
    #         if not file_type:
    #             raise ValueError("Processing information provided without a corresponding file_type.")

    #         # Validate processing against the file_type
    #         if file_type == "stream":
    #             StreamProcessingInfo(**processing)  # This will raise an error if not valid
    #         elif file_type == "CSV":
    #             CSVProcessingInfo(**processing)
    #         elif file_type == "TXT":
    #             TXTProcessingInfo(**processing)
    #         elif file_type == "JSON":
    #             JSONProcessingInfo(**processing)
    #         elif file_type == "NetCDF":
    #             NetCDFProcessingInfo(**processing)
    #         else:
    #             raise ValueError(f"Unsupported file_type: {file_type}")

    #     # Ensure that if file_type is changed, processing is provided and valid
    #     if file_type and not processing:
    #         raise ValueError("File type is changed but no corresponding processing information is provided.")
        
    #     return values
