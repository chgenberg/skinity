from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..database import get_session
from ..models import Provider
from ..crud import list_providers, create_provider, get_provider_by_id

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/", response_model=List[Provider])
def get_providers(
    country: str | None = None,
    tag: str | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
):
    return list_providers(session, country=country, tag=tag, q=q, limit=limit, offset=offset)


@router.get("/{provider_id}", response_model=Provider)
def get_provider(provider_id: int, session: Session = Depends(get_session)):
    provider = get_provider_by_id(session, provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.post("/", response_model=Provider)
def post_provider(provider: Provider, session: Session = Depends(get_session)):
    return create_provider(session, provider) 