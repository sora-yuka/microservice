from datetime import datetime, timezone

from fastapi import HTTPException, status

from ..models.promocode import PromoCode, DiscountType
from ..models.product import CartItem


class PromoValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def calculate_subtotal(items: list[CartItem]) -> float:
    return round(sum(float(item.product.price) * item.quantity for item in items), 2)


def validate_promo(promo: PromoCode | None, subtotal: float) -> None:
    if promo is None:
        raise PromoValidationError("Promo could not found")

    if not promo.is_active:
        raise PromoValidationError("Promo code is inactive")

    now = datetime.now(timezone.utc)
    if not (promo.valid_from <= now <= promo.valid_until):
        raise PromoValidationError("Promo code is expired or not yet valid")

    if promo.usage_limit is not None and promo.times_used >= promo.usage_limit:
        raise PromoValidationError("Promo code usage limit reached")

    if subtotal < float(promo.min_cart_total):
        raise PromoValidationError(
            f"Cart total must at least {promo.min_cart_total} to use this code"
        )


def calculate_discount(promo: PromoCode, subtotal: float) -> float:
    if promo.discount_type == DiscountType.PERCENTAGE:
        discount = subtotal * (float(promo.value) / 100)
    else:
        discount = float(promo.value)

    return round(discount, 2)
