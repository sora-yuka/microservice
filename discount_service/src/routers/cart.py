from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..auth import CurrentUserDep
from ..core.database import SessionDep
from ..models.product import Cart, CartItem, Product
from ..models.promocode import PromoCode
from ..schemas.discount import (
    CartOut,
    CartItemOut,
    AddCartItemRequest,
    UpdateCartItemRequest,
    PromoRequest,
    ApplyPromoResponse,
)
from ..services.promo import calculate_subtotal, validate_promo, calculate_discount

router = APIRouter(prefix="/cart", tags=["cart"])


async def _get_or_create_cart(session: SessionDep, user_id: int) -> Cart:
    result = await session.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    cart = result.scalar_one_or_none()
    if cart is None:
        cart = Cart(user_id=user_id)
        session.add(cart)
        await session.commit()
        await session.refresh(cart, attribute_names=["items"])
    return cart


def _serialize_cart(cart: Cart) -> CartOut:
    items = [
        CartItemOut(
            id=item.id,
            product_id=item.product_id,
            product=item.product.name,
            unit_price=float(item.product.price),
            quantity=item.quantity,
            line_total=round(float(item.product.price) * item.quantity, 2),
        )
        for item in cart.items
    ]
    subtotal = round(sum(i.line_total for i in items), 2)
    return CartOut(id=cart.id, items=items, subtotal=subtotal)


@router.get("/items", response_model=CartOut)
async def view_cart(user: CurrentUserDep, session: SessionDep):
    cart = await _get_or_create_cart(session, user.id)
    return _serialize_cart(cart)


@router.post("/items", response_model=CartOut, status_code=status.HTTP_201_CREATED)
async def add_item(
    payload: AddCartItemRequest, user: CurrentUserDep, session: SessionDep
):
    product = await session.get(Product, payload.product_id)
    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    if product.stock < payload.quantity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not enough stock"
        )

    cart = await _get_or_create_cart(session, user.id)

    existing = next((i for i in cart.items if i.product_id == payload.product_id), None)
    if existing:
        existing.quantity += payload.quantity
    else:
        cart.items.append(
            CartItem(product_id=payload.product_id, quantity=payload.quantity)
        )

    await session.commit()
    cart = await _get_or_create_cart(session, user.id)
    return _serialize_cart(cart)


@router.patch("/items/{item_id}", response_model=CartOut)
async def update_item(
    item_id: int,
    payload: UpdateCartItemRequest,
    user: CurrentUserDep,
    session: SessionDep,
):
    cart = await _get_or_create_cart(session, user.id)
    item = next((i for i in cart.items if i.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not in cart")

    item.quantity = payload.quantity
    await session.commit()
    cart = await _get_or_create_cart(session, user.id)
    return _serialize_cart(cart)


@router.delete("/items/{item_id}", response_model=CartOut)
async def delete_item(item_id: int, user: CurrentUserDep, session: SessionDep):
    cart = await _get_or_create_cart(session, user.id)
    item = next((i for i in cart if i.id == item_id), None)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not in cart"
        )

    await session.delete(item)
    await session.commit()
    cart = await _get_or_create_cart(session, user.id)
    return _serialize_cart(cart)


@router.post("/apply-promo", response_model=ApplyPromoResponse)
async def apply_promo(payload: PromoRequest, user: CurrentUserDep, session: SessionDep):
    cart = await _get_or_create_cart(session, user.id)
    if not cart.items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart is empty")
    subtotal = calculate_subtotal(cart.items)

    result = await session.execute(
        select(PromoCode).where(PromoCode.code == payload.promo_code)
    )
    promo = result.scalar_one_or_none()

    validate_promo(promo, subtotal)
    discount = calculate_discount(promo, subtotal)
    print(discount)

    return ApplyPromoResponse(
        subtotal=subtotal,
        discount_amount=discount,
        final_total=round(subtotal - discount, 2),
        promo_code=promo.code,
    )
