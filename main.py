"""API with pagination with page and size params."""
from enum import Enum
import math
from typing import List, Optional, Union
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

# Initialize the FastAPI app
app = FastAPI(
    title="RESTful API with Pagination",
    version="1.0.0",
    description=
    "An example of a RESTful API with pagination and OpenAPI 3.1 documentation",
    openapi_version="3.1.0",
)

# Sample data
ITEMS = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]


# Pydantic model for item
class Item(BaseModel):
    id: int
    name: str


# Pydantic model for paginated response
class PaginatedResponse(BaseModel):
    items: List[Item]
    total: int
    page: int
    size: int
    total_pages: int


class Cat(BaseModel):
    petType: str
    name: str
    favoriteToy: str

    @field_validator("petType")
    def validate_pet_type(cls, v):
        if v != "cat":
            raise ValueError("petType must be 'cat'")
        return v


class Dog(BaseModel):
    petType: str
    name: str
    breed: str

    @field_validator("petType")
    def validate_pet_type(cls, v):
        if v != "dog":
            raise ValueError("petType must be 'dog'")
        return v


# Use Union to represent anyOf logic
class Pet(BaseModel):
    pet: Union[Cat, Dog]


# Models for oneOf example
class ShapeType(str, Enum):
    RECTANGLE = "rectangle"
    CIRCLE = "circle"


class ShapeBase(BaseModel):
    shape_type: ShapeType
    color: Optional[str] = Field(
        None, pattern="^#[0-9a-fA-F]{6}$")  # Hex color validation
    name: Optional[str] = Field(None, min_length=1, max_length=50)


class Rectangle(ShapeBase):
    shape_type: ShapeType = ShapeType.RECTANGLE
    width: float = Field(..., gt=0,
                         le=1000)  # greater than 0, less than or equal to 1000
    height: float = Field(..., gt=0, le=1000)
    aspect_ratio: Optional[float] = None

    @field_validator('aspect_ratio', mode='before')
    @classmethod
    def calculate_aspect_ratio(cls, v, info):
        values = info.data
        if 'width' in values and 'height' in values:
            return round(values['width'] / values['height'], 2)
        return v

    @field_validator('width', 'height')
    @classmethod
    def validate_dimensions(cls, v):
        if not float(v).is_integer() and len(str(float(v)).split('.')[-1]) > 2:
            raise ValueError('Maximum 2 decimal places allowed')
        return v


class Circle(ShapeBase):
    shape_type: ShapeType = ShapeType.CIRCLE
    radius: float = Field(..., gt=0,
                          le=500)  # greater than 0, less than or equal to 500
    circumference: Optional[float] = None
    area: Optional[float] = None

    @field_validator('radius')
    @classmethod
    def validate_radius(cls, v):
        if not float(v).is_integer() and len(str(float(v)).split('.')[-1]) > 2:
            raise ValueError('Maximum 2 decimal places allowed')
        return v

    @model_validator(mode='after')
    def calculate_circle_properties(self) -> 'Circle':
        radius = self.radius
        self.circumference = round(2 * math.pi * radius, 2)
        self.area = round(math.pi * radius**2, 2)
        return self


class OneOfShape(BaseModel):
    shape: Union[Rectangle, Circle]

    @field_validator('shape')
    @classmethod
    def validate_shape_properties(cls, v):
        # Additional custom validation rules
        if isinstance(v, Rectangle):
            # Validate rectangle is not too narrow
            min_dimension = min(v.width, v.height)
            max_dimension = max(v.width, v.height)
            if max_dimension / min_dimension > 10:
                raise ValueError("Rectangle aspect ratio cannot exceed 10:1")

        if isinstance(v, Circle):
            # Validate circle size constraints
            if v.area > 785000:  # approximately pi * 500^2
                raise ValueError("Circle area exceeds maximum allowed size")

        return v


# New AllOf example
class BaseProduct(BaseModel):
    id: str = Field(..., pattern="^[A-Z]{2}[0-9]{6}$")  # Format: XX123456
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)


class InventoryItem(BaseModel):
    stock_count: int = Field(..., ge=0)
    warehouse_location: str = Field(
        ..., pattern="^[A-Z]-[0-9]{2}-[0-9]{2}$")  # Format: A-01-02
    reorder_point: int = Field(..., ge=0)


class ShippingDetails(BaseModel):
    weight_kg: float = Field(..., gt=0, le=1000)
    dimensions_cm: tuple[float, float,
                         float] = Field(...)  # (length, width, height)
    fragile: bool = False

    @field_validator('dimensions_cm')
    @classmethod
    def validate_dimensions(cls, v):
        if len(v) != 3 or not all(0 < x <= 300 for x in v):
            raise ValueError(
                "Dimensions must be 3 positive values, each ≤ 300cm")
        return v


# AllOf combines all three schemas - must satisfy ALL requirements
class CompleteProduct(BaseProduct, InventoryItem, ShippingDetails):

    @model_validator(mode='after')
    def validate_complete_product(self) -> 'CompleteProduct':
        # Calculate volume and validate against weight
        length, width, height = self.dimensions_cm
        volume_m3 = (length * width * height) / 1_000_000  # convert to m³

        # Density check (weight/volume ratio)
        density = self.weight_kg / volume_m3
        if density > 2000:  # Max density 2000 kg/m³
            raise ValueError("Product density exceeds maximum allowed")

        # Validate reorder point against price
        if self.reorder_point * self.price > 10000:
            raise ValueError(
                "Total reorder value exceeds maximum allowed (10000)")

        return self


@app.post("/pets", response_description="Add a new pet", response_model=Pet)
async def add_pet(pet: Pet):
    """
    Add a new pet to the system.

    - **pet**: The pet to add (either a cat or a dog).
    """
    try:
        # Validate the pet input based on its type (Cat or Dog)
        pet_data = pet.pet.model_dump()
        return {"message": "Pet added successfully", "pet": pet_data}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors()) from e

class ResponseVerbosity(str, Enum):
    MINIMUM = "minimum"
    REGULAR = "regular"
    EXTENDED = "extended"

# Base schemas for different verbosity levels
class LaptopBase(BaseModel):
    id: str = Field(..., description="Unique identifier for the laptop")
    brand: str
    model: str
    price: float


class LaptopRegular(BaseModel):
    id: str = Field(..., description="Unique identifier for the laptop")
    brand: str
    model: str
    price: float
    processor: str
    ram_gb: int
    storage_gb: int
    screen_size: float
    operating_system: str
    in_stock: bool


class LaptopExtended(LaptopRegular):
    graphics_card: str
    battery_whr: int
    weight_kg: float
    dimensions_cm: tuple[float, float, float]  # length, width, height
    ports: List[str]
    warranty_months: int
    release_date: datetime
    last_updated: datetime
    description: str
    features: List[str]
    reviews_count: int
    average_rating: float

# Sample data
SAMPLE_LAPTOP = [{
    "id": "LP123456",
    "brand": "TechBook",
    "model": "Pro X15",
    "price": 1299.99,
    "processor": "Intel Core i7 12700H",
    "ram_gb": 16,
    "storage_gb": 512,
    "screen_size": 15.6,
    "operating_system": "Windows 11 Pro",
    "in_stock": True,
    "graphics_card": "NVIDIA RTX 3060 6GB",
    "battery_whr": 80,
    "weight_kg": 2.1,
    "dimensions_cm": (35.8, 24.2, 1.9),
    "ports": ["USB-C", "USB-A", "HDMI", "Audio Jack"],
    "warranty_months": 24,
    "release_date": datetime(2023, 6, 15),
    "last_updated": datetime(2024, 1, 15),
    "description": "Professional grade laptop for demanding users",
    "features": ["Backlit Keyboard", "Fingerprint Reader", "Thunderbolt 4"],
    "reviews_count": 128,
    "average_rating": 4.5
},{
        "id": "LP789101",
        "brand": "FutureComp",
        "model": "Vision Z14",
        "price": 1599.99,
        "processor": "AMD Ryzen 9 6900HX",
        "ram_gb": 32,
        "storage_gb": 1024,
        "screen_size": 14.0,
        "operating_system": "Windows 11 Home",
        "in_stock": True,
        "graphics_card": "AMD Radeon 680M",
        "battery_whr": 76,
        "weight_kg": 1.8,
        "dimensions_cm": (32.1, 22.0, 1.7),
        "ports": ["USB-C", "HDMI", "Audio Jack"],
        "warranty_months": 36,
        "release_date": datetime(2023, 9, 10),
        "last_updated": datetime(2024, 1, 12),
        "description": "Ultra-lightweight laptop with powerful performance",
        "features": ["Face Recognition", "Wi-Fi 6E", "OLED Display"],
        "reviews_count": 89,
        "average_rating": 4.7,
    },
    {
        "id": "LP567812",
        "brand": "ProCompute",
        "model": "Elite G17",
        "price": 1899.99,
        "processor": "Intel Core i9 12900H",
        "ram_gb": 64,
        "storage_gb": 2048,
        "screen_size": 17.3,
        "operating_system": "Windows 11 Pro",
        "in_stock": False,
        "graphics_card": "NVIDIA RTX 4080 12GB",
        "battery_whr": 99,
        "weight_kg": 3.2,
        "dimensions_cm": (39.6, 26.5, 2.1),
        "ports": ["USB-C", "USB-A", "HDMI", "Ethernet"],
        "warranty_months": 12,
        "release_date": datetime(2022, 11, 20),
        "last_updated": datetime(2024, 1, 10),
        "description": "High-performance gaming and workstation laptop",
        "features": ["4K Display", "RGB Keyboard", "Thunderbolt 4"],
        "reviews_count": 345,
        "average_rating": 4.6,
    },
    {
        "id": "LP345678",
        "brand": "MegaWorks",
        "model": "SwiftEdge S13",
        "price": 899.99,
        "processor": "Intel Core i5 12450H",
        "ram_gb": 8,
        "storage_gb": 256,
        "screen_size": 13.3,
        "operating_system": "Windows 11 Home",
        "in_stock": True,
        "graphics_card": "Intel Iris Xe",
        "battery_whr": 58,
        "weight_kg": 1.2,
        "dimensions_cm": (30.5, 21.2, 1.5),
        "ports": ["USB-C", "HDMI", "MicroSD"],
        "warranty_months": 12,
        "release_date": datetime(2023, 3, 25),
        "last_updated": datetime(2024, 1, 5),
        "description": "Compact laptop ideal for students and professionals",
        "features": ["Touchscreen", "Lightweight Design", "Fast Charging"],
        "reviews_count": 256,
        "average_rating": 4.3,
    }]

@app.post("/shapes/oneof")
async def create_shape(shape_data: OneOfShape):
    """
    oneOf example with strict validation:
    - Validates shape type using enum
    - Enforces dimension limits
    - Validates decimal precision
    - Calculates derived properties
    - Enforces aspect ratio limits
    - Validates color format
    - Validates name length
    """
    shape = shape_data.shape
    response = {
        "message":
        f"{shape.shape_type.value.capitalize()} created successfully",
        "shape": shape,
        "validation_details": {
            "valid_color": shape.color is None or shape.color.startswith("#"),
            "dimensions_within_limits": True
        }
    }

    if isinstance(shape, Rectangle):
        response["validation_details"].update({
            "aspect_ratio":
            shape.aspect_ratio,
            "area":
            round(shape.width * shape.height, 2)
        })
    elif isinstance(shape, Circle):
        response["validation_details"].update({
            "circumference": shape.circumference,
            "area": shape.area
        })

    return response


@app.get("/items", response_model=PaginatedResponse, tags=["Items"])
async def get_items(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    size: int = Query(10,
                      ge=1,
                      le=50,
                      description="Number of items per page (max 50)"),
):
    """
    Get a paginated list of items.
    """
    total_items = len(ITEMS)
    start = (page - 1) * size
    end = start + size

    if start >= total_items:
        raise HTTPException(status_code=404, detail="Page not found")

    paginated_items = ITEMS[start:end]
    total_pages = (total_items + size - 1) // size

    return PaginatedResponse(
        items=paginated_items,
        total=total_items,
        page=page,
        size=size,
        total_pages=total_pages,
    )


@app.post("/products/allof")
async def create_product(product: CompleteProduct):
    """
    allOf example: Product must satisfy ALL requirements from:
    - BaseProduct (ID, name, price)
    - InventoryItem (stock, location, reorder point)
    - ShippingDetails (weight, dimensions, fragility)
    """
    volume_m3 = math.prod(product.dimensions_cm) / 1_000_000

    return {
        "message": "Product created successfully",
        "product": product,
        "calculated_metrics": {
            "volume_m3": round(volume_m3, 3),
            "density_kg_m3": round(product.weight_kg / volume_m3, 2),
            "reorder_value": product.reorder_point * product.price
        }
    }

@app.get(
    "/laptops/{laptop_id}",
    responses={
        200: {
            "description": "Successful response with laptop details",
            "content": {
                "application/json": {
                    "examples": {
                        "minimum": {
                            "value": {
                                "id": "LP123456",
                                "brand": "TechBook",
                                "model": "Pro X15",
                                "price": 1299.99
                            }
                        },
                        "regular": {
                            "value": {
                                "id": "LP123456",
                                "brand": "TechBook",
                                "model": "Pro X15",
                                "price": 1299.99,
                                "processor": "Intel Core i7 12700H",
                                "ram_gb": 16,
                                "storage_gb": 512,
                                "screen_size": 15.6,
                                "operating_system": "Windows 11 Pro",
                                "in_stock": True
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_laptop(
    laptop_id: str,
    verbosity: ResponseVerbosity = Query(
        ResponseVerbosity.REGULAR,
        description="Control the verbosity level of the response"
    )
):
    """
    Get laptop details with configurable verbosity level:
    - minimum: Basic info (id, brand, model, price)
    - regular: Common specs (adds processor, RAM, storage, etc.)
    - extended: All details (adds graphics, dimensions, features, etc.)
    """
    # In real app, fetch from database based on laptop_id
    laptop_data = SAMPLE_LAPTOP[0]

    if verbosity == ResponseVerbosity.MINIMUM:
        return LaptopBase(**{
            k: laptop_data[k]
            for k in LaptopBase.__annotations__.keys()
        })

    elif verbosity == ResponseVerbosity.REGULAR:
        return LaptopRegular(**{
            k: laptop_data[k]
            for k in LaptopRegular.__annotations__.keys()
        })

    else:  # EXTENDED
        return LaptopExtended(**laptop_data)

# Additional endpoint for bulk retrieval with verbosity
@app.get("/laptops")
async def list_laptops(
    verbosity: ResponseVerbosity = Query(
        ResponseVerbosity.REGULAR,
        description="Control the verbosity level of the response"
    ),
    limit: int = Query(2, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List laptops with configurable verbosity level.
    Supports pagination through limit and offset parameters.
    """
    # In real app, fetch from database with pagination
    laptops = SAMPLE_LAPTOP  # Sample data

    if verbosity == ResponseVerbosity.MINIMUM:
        return [
            LaptopBase(**{k: l[k] for k in LaptopBase.__annotations__.keys()})
            for l in laptops
        ]

    elif verbosity == ResponseVerbosity.REGULAR:
        return [
            LaptopRegular(**{k: l[k] for k in LaptopRegular.__annotations__.keys()})
            for l in laptops
        ]

    else:  # EXTENDED
        return [LaptopExtended(**l) for l in laptops]
