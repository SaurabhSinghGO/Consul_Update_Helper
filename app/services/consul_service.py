from typing import Dict, List, Any
import requests
import base64
from fastapi import HTTPException

class ConsulService:
    def __init__(self, setup_name: str, service_name: str):
        self.setup_name = setup_name
        self.service_name = service_name
        self.base_url = f'https://{setup_name}-consul.greymatter.greyorange.com/v1/kv/config/{service_name}'
        self.headers = {'Content-Type': 'application/json'}

    def validate_setup(self) -> bool:
        try:
            url = f"https://{self.setup_name}-consul.greymatter.greyorange.com/ui/dc1/kv"
            response = requests.get(url, headers=self.headers, timeout=5)
            return response.status_code == 200
        except Exception:
            return False
            
    def get_available_services(self) -> List[str]:
        try:
            url = f'https://{self.setup_name}-consul.greymatter.greyorange.com/v1/kv/config/?keys=true'
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"Error fetching services: {response.text}")
                return []
            
            services = []
            for key in response.json():
                parts = key.split('/')
                if len(parts) >= 2 and parts[0] == 'config' and parts[1]:
                    service_name = parts[1] 
                    if service_name and service_name not in services:
                        services.append(service_name)
            
            return services
        except Exception as e:
            print(f"Error retrieving services for {self.setup_name}: {e}")
            return []

    def get_all_keys(self) -> Dict[str, str]:
        try:
            url = f"{self.base_url}?recurse=true"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"Error fetching keys: {response.text}")
                return {}
            
            results = {}
            for item in response.json():
                key = item['Key'].split('/')[-1]
                value = base64.b64decode(item['Value']).decode('utf-8') if item.get('Value') else ''
                # print(f"key : {key} ,  value : {value}")
                if not key.strip(): #if not then returns empty key val pair as first property while fetching 
                    continue
                
                results[key] = value
            
            return results
        except Exception as e:
            print(f"Error retrieving keys for {self.service_name} in {self.setup_name}: {e}")
            return {}

    def set_key_value(self, key: str, value: Any) -> bool:
        try:
            url = f"{self.base_url}/{key}"
            response = requests.put(url, headers=self.headers, data=str(value))
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Error setting key-value for {self.service_name} in {self.setup_name}: {e}")
            return False