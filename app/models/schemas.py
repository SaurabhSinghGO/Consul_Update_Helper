from pydantic import BaseModel
from typing import Dict, Any, Optional

class ConsulServiceProperties(BaseModel):
    setup_name: str
    service_name: str
    data: Dict[str, Any]

class TransferPropertiesRequest(BaseModel):
    source_setup: str
    destination_setup: str
    service_name: str

class ComparePropertiesRequest(BaseModel):
    source_setup: str
    destination_setup: str
    service_name: str

class ConsulPropertiesResponse(BaseModel):
    message: str
    data: Dict[str, Any]
    setup_name: str
    service_names: Optional[list[str]] = None

class TransferResponse(BaseModel):
    message: str
    source_setup: str
    destination_setup: str
    results: Dict[str, Any]

class CompareResponse(BaseModel):
    source_setup: str
    destination_setup: str
    results: Dict[str, Any]