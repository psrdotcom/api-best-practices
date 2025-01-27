# Simple Python FastAPI Collection
To explain the concepts of OpenAPI 3.1.x, created a few APIs

## Configuration
### Pre-requisites
1. Bruno App
2. Install Pydantic, FastAPI, UniCorn
   1. ```sh
      pip install -r requirements.txt


## Run the application on a local http server
```sh
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
## Usage
### /pets
/pets is an endpoint to handle pets that can be either a "cat" or a "dog". Here's how it works:

#### Validation: 
The Cat and Dog classes validate their attributes, ensuring the correct petType and other required fields.
#### Union for anyOf: 
The Pet class uses Union[Cat, Dog] to allow the input to be either a cat or a dog.
#### POST Endpoint:
#### URL: /pets
Validates the input and returns the pet's details if it's valid.
If the input doesn't match the schema, it raises a 400 error.
##### Request Body
```json
{
  "pet": {
    "petType": "cat",
    "name": "Whiskers",
    "favoriteToy": "Softball"
  }
}
```
```json
{
  "pet": {
    "petType": "dog",
    "name": "Buddy",
    "breed": "Golden Retriever"
  }
}
```

## Contact
sureshraju.pilli@gmail.com
