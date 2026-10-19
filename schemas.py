from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str
    price: float = Field(gt=0)

class ProductPatch(BaseModel):
    name: str | None = None
    price: float | None = Field(default=None, gt=0)

class ProductDBResponse(BaseModel):
    id: int
    name: str
    price: float