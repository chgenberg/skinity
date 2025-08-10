from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..database import get_session, engine
from ..crud import list_providers, list_products

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/")
def search(
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    tag: str | None = None,
    skin_type: str | None = None,
    ingredient: str | None = None,
    limit: int = 25,
    offset: int = 0,
    session: Session = Depends(get_session),
) -> Dict[str, List[Any]]:
    try:
        providers = list_providers(session, q=q, limit=limit, offset=offset)
    except Exception:
        providers = []
    try:
        products = list_products(
            session,
            q=q,
            min_price=min_price,
            max_price=max_price,
            tag=tag,
            skin_type=skin_type,
            ingredient=ingredient,
            limit=limit,
            offset=offset,
        )
    except Exception:
        products = []
    return {"providers": providers, "products": products}


@router.get("/products")
def search_products(
    q: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    tag: str | None = None,
    skin_type: str | None = None,
    ingredient: str | None = None,
    limit: int = 25,
    offset: int = 0,
) -> Dict[str, List[Any]]:
    try:
        with Session(engine) as session:
            products = list_products(
                session,
                q=q,
                min_price=min_price,
                max_price=max_price,
                tag=tag,
                skin_type=skin_type,
                ingredient=ingredient,
                limit=limit,
                offset=offset,
            )
    except Exception as e:
        # Return empty list plus error hint to avoid 500 for the UI
        return {"providers": [], "products": [], "error": str(e)}
    return {"providers": [], "products": products}


@router.get("/ping")
def search_ping():
    return {"ok": True} 