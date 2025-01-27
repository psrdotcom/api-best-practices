import json
import requests
import yaml

# Fetch the OpenAPI JSON schema from the running FastAPI application
response = requests.get("http://127.0.0.1:8000/openapi.json")
openapi_json = response.json()

# Load the local openapi.yaml file
with open("doc/openapi.yaml", "r", encoding="utf-8") as f:
    openapi_yaml = yaml.safe_load(f)

# Convert the YAML to JSON for comparison
openapi_yaml_json = json.loads(json.dumps(openapi_yaml))

# Compare the two schemas
if openapi_json == openapi_yaml_json:
    print("The OpenAPI specification matches the implementation in app.py")
else:
    print("The OpenAPI specification does not match the implementation in app.py")
