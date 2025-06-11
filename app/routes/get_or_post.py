from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Dict, Any, List
from app.services.consul_service import ConsulService

router = APIRouter()

class ConsulPropertiesRequest(BaseModel):
    setup_name: str
    service_name: str
    data: Dict[str, Any] = {}


@router.get("/api/v1/consul/properties")
async def get_consul_properties(setup_name: str, service_name: str):
    if not setup_name or not service_name:
        raise HTTPException(status_code=400, detail="Both 'setup_name' and 'service_name' query parameters are required.")
    
    consul_validator = ConsulService(setup_name, "")
    if not consul_validator.validate_setup():
        raise HTTPException(status_code=404, detail=f"Error: Setup '{setup_name}' is not accessible.")
    
    available_services = consul_validator.get_available_services()
    
    if service_name.lower() == "all":
        if not available_services:
            raise HTTPException(status_code=404, detail=f"No services found in setup '{setup_name}'")
        
        result = {}
        for service in available_services:
            consul_service = ConsulService(setup_name, service)
            properties = consul_service.get_all_keys()
            if properties:
                result[service] = properties
        
        return {
            "message": f"All Consul Variables Fetched for {len(result)} services",
            "data": result,
            "setup_name": setup_name,
            "service_names": list(result.keys())
        }
    
    service_names = [name.strip() for name in service_name.split(',')]
    result = {}
    invalid_services = []
    
    for service in service_names:
        if service not in available_services:
            invalid_services.append(service)
    
    if invalid_services:
        raise HTTPException(status_code=404, detail=f"Error: Services not found: {', '.join(invalid_services)}")
    
    for service in service_names:
        consul_service = ConsulService(setup_name, service)
        properties = consul_service.get_all_keys()
        result[service] = properties
    
    return {
        "message": "All Consul Variables Fetched",
        "data": result,
        "setup_name": setup_name,
        "service_names": service_names
    }

@router.post("/api/v1/consul/properties")
async def set_consul_properties(request: ConsulPropertiesRequest = Body(..., example={"setup_name": "string", "service_name": "string", "data": {"service1-name": {"key1": "val1"}, "service2-name": {"key2": "val2"}}})):
    setup_name = request.setup_name
    service_name = request.service_name
    data = request.data
    
    if not setup_name or not service_name:
        raise HTTPException(status_code=400, detail="Both 'setup_name' and 'service_name' are required in the request body.")
    
    consul_validator = ConsulService(setup_name, "")
    if not consul_validator.validate_setup():
        raise HTTPException(status_code=404, detail=f"Error: Setup '{setup_name}' is not accessible.")
    
    if not data or not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Invalid input. Expecting a dictionary of services and their properties.")
    
    results = {}
    
    for service in data:
        service_data = data[service]
        if not isinstance(service_data, dict):
            results[service] = {"status": "error", "message": "Invalid data format. Expected dictionary"}
            continue
        
        consul_service = ConsulService(setup_name, service)
        
        for key, value in service_data.items():
            consul_service.set_key_value(key, value)
        
        results[service] = {
            "status": "success" 
        }
    
    return {
        "message": "Consul Properties Updated",
        "results": results,
        "setup_name": setup_name,
        "service_names": list(data.keys())
    }

    source_setup = request.source_setup
    destination_setup = request.destination_setup
    service_name = request.service_name

    if not source_setup or not destination_setup or not service_name:
        raise HTTPException(status_code=400, detail="All three 'source_setup', 'destination_setup', and 'service_name' are required in the request body.")
    
    source_validator = ConsulService(source_setup, "")
    if not source_validator.validate_setup():
        raise HTTPException(status_code=404, detail=f"Error: Source setup '{source_setup}' is not accessible.")
    
    dest_validator = ConsulService(destination_setup, "")
    if not dest_validator.validate_setup():
        raise HTTPException(status_code=404, detail=f"Error: Destination setup '{destination_setup}' is not accessible.")
    
    source_services = source_validator.get_available_services()
    
    if service_name not in source_services:
        raise HTTPException(status_code=404, detail=f"Error: Service '{service_name}' not found in source setup.")
    
    source_consul = ConsulService(source_setup, service_name)
    all_properties = source_consul.get_all_keys()
    
    if not all_properties:
        raise HTTPException(status_code=404, detail=f"No properties found in source setup for service '{service_name}'")
    
    destination_consul = ConsulService(destination_setup, service_name)
    
    for key, value in all_properties.items():
        destination_consul.set_key_value(key, value)
    
    return {
        "message": f"Transferred properties from '{source_setup}' to '{destination_setup}'",
        "source_setup": source_setup,
        "destination_setup": destination_setup,
        "properties": all_properties
    }

    source_setup = request.source_setup
    destination_setup = request.destination_setup
    service_name = request.service_name
    
    if not source_setup or not destination_setup or not service_name:
        raise HTTPException(status_code=400, detail="All three parameters required")
    
    source_validator = ConsulService(source_setup, "")
    if not source_validator.validate_setup():
        raise HTTPException(status_code=404, detail=f"Error: Source setup '{source_setup}' is not accessible.")
    
    dest_validator = ConsulService(destination_setup, "")
    if not dest_validator.validate_setup():
        raise HTTPException(status_code=404, detail=f"Error: Destination setup '{destination_setup}' is not accessible.")
    
    source_services = source_validator.get_available_services()
    dest_services = dest_validator.get_available_services()
    
    if service_name.lower() == "all":
        all_services = list(set(source_services) | set(dest_services))
        if not all_services:
            raise HTTPException(status_code=404, detail="No services found in either setup")
        service_names = all_services
    else:
        service_names = [name.strip() for name in service_name.split(',')]
        
        invalid_services = []
        for service in service_names:
            if service not in source_services and service not in dest_services:
                invalid_services.append(service)
        
        if invalid_services:
            raise HTTPException(status_code=404, detail=f"Error: Services not found in either setup: {', '.join(invalid_services)}")
    
    results = {}
    
    for service in service_names:
        consul_service_1 = ConsulService(source_setup, service)
        properties_1 = consul_service_1.get_all_keys()
        
        consul_service_2 = ConsulService(destination_setup, service)
        properties_2 = consul_service_2.get_all_keys()
        
        if not properties_1 and not properties_2:
            results[service] = {
                "status": "error",
                "message": f"Service '{service}' does not exist in either setup"
            }
            continue
        
        if not properties_1:
            properties_1 = {}
        if not properties_2:
            properties_2 = {}
        
        keys_1 = set(properties_1.keys())
        keys_2 = set(properties_2.keys())

        source_exclusive = {key: properties_1[key] for key in keys_1 - keys_2}
        destination_exclusive = {key: properties_2[key] for key in keys_2 - keys_1}
        
        common_keys = keys_1 & keys_2
        different_values = {}
        
        for key in common_keys:
            if properties_1[key] != properties_2[key]:
                different_values[key] = {
                    f"{source_setup}": properties_1[key],
                    f"{destination_setup}": properties_2[key]
                }
        
        results[service] = {
            f"exclusive_to_{source_setup}": source_exclusive,
            f"exclusive_to_{destination_setup}": destination_exclusive,
            "common_keys_with_different_values": different_values
        }
    
    return {
        "source_setup": source_setup,
        "destination_setup": destination_setup,
        "results": results
    }