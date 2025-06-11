from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services.consul_service import ConsulService

router = APIRouter()

class CompareRequest(BaseModel):
    source_setup: str
    destination_setup: str
    service_name: str

@router.get("/api/v1/consul/properties/compare", response_model=dict)
async def compare_properties_between_two_setups(
    source_setup: str = Query(...),
    destination_setup: str = Query(...),
    service_name: str = Query(...)
):
    try:
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
            invalid_services = [name for name in service_names if name not in source_services and name not in dest_services]
            if invalid_services:
                raise HTTPException(status_code=404, detail=f"Error: Services not found in either setup: {', '.join(invalid_services)}")
        
        results = {}
        
        for service_name in service_names:
            consul_service_1 = ConsulService(source_setup, service_name)
            properties_1 = consul_service_1.get_all_keys()
            
            consul_service_2 = ConsulService(destination_setup, service_name)
            properties_2 = consul_service_2.get_all_keys()
            
            if not properties_1 and not properties_2:
                results[service_name] = {
                    "status": "error",
                    "message": f"Service '{service_name}' does not exist in either setup"
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
            
            results[service_name] = {
                f"exclusive_to_{source_setup}": source_exclusive,
                f"exclusive_to_{destination_setup}": destination_exclusive,
                "common_keys_with_different_values": different_values
            }
        
        return JSONResponse(content={
            "source_setup": source_setup,
            "destination_setup": destination_setup,
            "results": results
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")