from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, update

from ..auth import CurrentUserDep, require_staff
from ..core.database import SessionDep
from ..models.product import Product
from ..models.promocode import PromoCode
from ..schemas.product import ProductOut, ProductCreate, UpdateProduct
from ..schemas.discount import PromoCodeCreate, PromoCodeOut, UpdatePromoCode

router = APIRouter(
    prefix="/admin", tags=["admin"], dependencies=[Depends(require_staff)]
)


@router.post(
    "/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED
)
async def create_product(
    payload: ProductCreate, session: SessionDep, user: CurrentUserDep
):
    product = Product(**payload.model_dump())
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.patch("/products", response_model=ProductOut)
async def update_product(
    product_id: int, payload: UpdateProduct, session: SessionDep, user: CurrentUserDep
):
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return product
    stmt = (
        update(Product)
        .where(Product.id == product_id)
        .values(**updates)
        .returning(Product)
    )
    result = await session.execute(stmt)
    updated_product = result.scalar_one()
    await session.commit()
    return updated_product


@router.post(
    "/promo-codes", response_model=PromoCodeOut, status_code=status.HTTP_201_CREATED
)
async def create_promo_code(
    payload: PromoCodeCreate, session: SessionDep, user: CurrentUserDep
):
    promo = PromoCode(**payload.model_dump(exclude_unset=True))
    session.add(promo)
    await session.commit()
    await session.refresh(promo)
    return promo


@router.patch("/promo-codes/{promo_id}", response_model=PromoCodeOut)
async def update_promo_code(
    promo_id: int, payload: UpdatePromoCode, session: SessionDep, user: CurrentUserDep
):
    promo = await session.get(PromoCode, promo_id)
    if promo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Promo code not found"
        )
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return promo
    stmt = (
        update(PromoCode)
        .where(PromoCode.id == promo_id)
        .values(**updates)
        .returning(PromoCode)
    )
    result = await session.execute(stmt)
    updated_promo = result.scalar_one()
    await session.commit()
    return updated_promo


@router.get("/promo-codes", response_model=list[PromoCodeOut])
async def list_promo_codes(session: SessionDep, user: CurrentUserDep):
    result = await session.execute(select(PromoCode))
    return result.scalars().all()
