from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from ..models.promocode import DiscountType


class CartItemOut(BaseModel):
    id: int
    product_id: int
    product: str
    unit_price: float
    quantity: int
    line_total: float


class CartOut(BaseModel):
    id: int
    items: list[CartItemOut]
    subtotal: float


class AddCartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(gt=0)


class PromoRequest(BaseModel):
    promo_code: str


class ApplyPromoResponse(BaseModel):
    subtotal: float
    discount_amount: float
    final_total: float
    promo_code: str


class PromoCodeCreate(BaseModel):
    code: str
    discount_type: DiscountType
    value: float = Field(gt=0)
    min_cart_total: float = Field(default=0, ge=0)
    usage_limit: int | None = None
    valid_from: datetime
    valid_until: datetime


class PromoCodeOut(PromoCodeCreate):
    id: int
    times_used: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UpdatePromoCode(BaseModel):
    code: str | None = None
    discount_type: DiscountType | None = None
    value: float | None = Field(default=None, gt=0)
    min_cart_total: float | None = Field(default=None, ge=0)
    usage_limit: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
