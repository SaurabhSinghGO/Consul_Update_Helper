# Consul Update FastAPI

This project is a FastAPI application that interacts with Consul to manage key-value properties across different setups. It provides endpoints for retrieving, setting, transferring, and comparing properties in Consul.

## Project Structure

```
consul_update_helper
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── models
│   │   └── schemas.py
│   ├── routes
│   │   ├── get_or_post.py
│   │   ├── transfer.py
│   │   └── compare.py
│   └── services
│       └── consul_service.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/SaurabhSinghGO/Consul_Update_Helper.git
   cd consul_update_helper
   ```

2. Create a virtual environment:
   ```
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the FastAPI application, execute the following command:

```
uvicorn app.main:app --host 0.0.0.0 --port 5003 --reload
```

You can access the API documentation at `http://localhost:5003/docs`.

## Endpoints

- **GET /api/v1/consul/properties**: Retrieve Consul properties.
- **POST /api/v1/consul/properties**: Set Consul properties.
- **POST /api/v1/consul/properties/transfer**: Transfer properties from one setup to another.
- **GET /api/v1/consul/properties/compare**: Compare properties between two setups.
  
