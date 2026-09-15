from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from ..core.database import SessionDep
from ..models.product import Product
from ..schemas.product import ProductOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductOut])
async def list_products(session: SessionDep):
    result = await session.execute(select(Product).where(Product.is_active == True))
    return result.scalars().all()


@router.get("/product_id", response_model=ProductOut)
async def get_product(product_id: int, session: SessionDep):
    product = await session.get(Product, product_id)
    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )
    return product
