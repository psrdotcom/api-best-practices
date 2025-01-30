# PSR And Apps - REST API best practices

## Objectives
- OpenAPI 3.1.0 specification for REST API best practices
- This API provides best practices for REST API design, including examples of anyOf, oneOf, and allOf in OpenAPI 3.1.x.
- Simple Python FastAPI Collection
- To explain the concepts of OpenAPI 3.1.x, created a few APIs

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
### Local
- Navigate the doc folder
- In Bruno App, use "Open Collection" option
- Browse to doc/APICollection
- This collection will have the APIs of anyOf, oneOf, allOf and Pagination
- To go through the API examples of "Entity Object Verbosity - Projection", open "APIProjection_LaptopExample/APIProjection" in Bruno
- Try all the valid and invalid API requests from the collection and modify to play around.

### SwaggerHub
- Want to try the same on the SwaggerHub then open the openapi.yaml file and choose the target server.
- Otherwise, use this public API: https://app.swaggerhub.com/apis/SURESHRAJUPILLI_1/api-best-practices/1.0.0-oas3-oas3.1

## API Information
### Info
   - Title: REST API best practices
   - Description: This API provides best practices for REST API design.
   - Version: 1.0.0-oas3-oas3.1
   - Contact: Suresh Raju Pilli (https://www.pillisureshraju.in/, sureshraju.pilli@gmail.com)

### Servers:
   - http://localhost:8000 (Testing server)
   - https://military-kesley-psrandapps-d7f588a1.koyeb.app (Main (Production) Server)

### Tags:
   - Pets: Examples of anyOf OpenAPI 3.1.x
   - Shapes: Examples of oneOf OpenAPI 3.1.x
   - Products: Examples of allOf OpenAPI 3.1.x
   - Items: Paginated items
   - Laptops: Entity Object Verbosity - Projection
 
### Paths:
   - /pets/anyof: Add a pet (either a cat or a dog)
   - /shapes/oneof: Create a shape (either a rectangle or circle with strict validation)
   - /products/allof: Create a product that must satisfy all schema requirements
   - /offsetitems: Get a paginated list of items using offset pagination
   - /cursoritems: Get a paginated list of items using cursor pagination
   - /laptops/{laptop_id}: Get laptop details with configurable verbosity level
   - /laptops: List laptops with pagination and verbosity control
 
### Components:
 - Schemas:
   - Cat: Schema for a cat
   - Dog: Schema for a dog
   - ShapeType: Enum for shape types (rectangle, circle)
   - ShapeBase: Base schema for shapes
   - Rectangle: Schema for a rectangle
   - Circle: Schema for a circle
   - OneOfShape: Schema for oneOf shape (rectangle or circle)
   - BaseProduct: Base schema for a product
   - InventoryItem: Schema for inventory item
   - ShippingDetails: Schema for shipping details
   - CompleteProduct: Schema for a complete product (allOf BaseProduct, InventoryItem, ShippingDetails)
   - OffsetItem: Schema for an offset item
   - CursorItem: Schema for a cursor item
   - PaginatedResponse: Schema for paginated response
   - ResponseVerbosity: Enum for response verbosity levels (minimum, regular, extended)
   - LaptopBase: Base schema for a laptop
   - LaptopRegular: Schema for a regular laptop (allOf LaptopBase)
   - LaptopExtended: Schema for an extended laptop (allOf LaptopRegular)
   - OneOfShapeErrorResponse: Schema for oneOf shape error response

## Contact
sureshraju.pilli@gmail.com
