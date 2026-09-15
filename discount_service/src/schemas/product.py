from pydantic import BaseModel, ConfigDict, Field


class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    stock: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str
    price: float = Field(gt=0)
    stock: int = Field(ge=0)


class UpdateProduct(BaseModel):
    name: str | None = None
    price: float | None = None
    stock: int | None = None
    is_active: bool | None = True
