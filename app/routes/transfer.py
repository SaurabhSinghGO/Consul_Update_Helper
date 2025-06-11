from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from app.services.consul_service import ConsulService

router = APIRouter()

class TransferRequest(BaseModel):
    source_setup: str
    destination_setup: str
    service_name: str

class TransferResponse(BaseModel):
    message: str
    source_setup: str
    destination_setup: str
    results: dict

@router.post("/api/v1/consul/properties/transfer")
async def transfer_consul_properties(request: TransferRequest = Body(..., example={"source_setup": "source_setup-name", "destination_setup": "destination_setup-name", "service_name": "service1-name, service2-name"})):
    try:
        source_setup = request.source_setup
        destination_setup = request.destination_setup
        service_name_param = request.service_name

        source_validator = ConsulService(source_setup, "")
        if not source_validator.validate_setup():
            raise HTTPException(status_code=404, detail=f"Error: Source setup '{source_setup}' is not accessible.")

        dest_validator = ConsulService(destination_setup, "")
        if not dest_validator.validate_setup():
            raise HTTPException(status_code=404, detail=f"Error: Destination setup '{destination_setup}' is not accessible.")

        source_services = source_validator.get_available_services()
        service_names = [name.strip() for name in service_name_param.split(',')]
        results = {}
        invalid_services = []

        for service_name in service_names:
            if service_name not in source_services:
                invalid_services.append(service_name)

        if invalid_services:
            raise HTTPException(status_code=404, detail=f"Error: Services not found in source setup: {', '.join(invalid_services)}")

        for service_name in service_names:
            source_consul = ConsulService(source_setup, service_name)
            all_properties = source_consul.get_all_keys()

            if not all_properties:
                results[service_name] = {
                    "status": "error",
                    "message": f"No properties found in source setup for this service"
                }
                continue

            destination_consul = ConsulService(destination_setup, service_name)

            for key, value in all_properties.items():
                destination_consul.set_key_value(key, value)

            results[service_name] = {
                "status": "success",
                "properties": all_properties
            }

        return TransferResponse(
            message=f"Transferred properties from '{source_setup}' to '{destination_setup}'",
            source_setup=source_setup,
            destination_setup=destination_setup,
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transferring Consul properties: {str(e)}")