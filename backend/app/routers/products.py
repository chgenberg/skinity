from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..database import get_session
from ..models import Product
from ..crud import list_products, create_product

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[Product])
def get_products(
    provider_id: int | None = None,
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    tag: str | None = None,
    skin_type: str | None = None,
    ingredient: str | None = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    return list_products(
        session,
        provider_id=provider_id,
        q=q,
        min_price=min_price,
        max_price=max_price,
        tag=tag,
        skin_type=skin_type,
        ingredient=ingredient,
        limit=limit,
        offset=offset,
    )


@router.post("/", response_model=Product)
def post_product(product: Product, session: Session = Depends(get_session)):
    return create_product(session, product) 