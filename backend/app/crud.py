from typing import Iterable, Optional, Sequence
from sqlmodel import Session, select
from .models import Provider, Product


# Provider CRUD

def create_provider(session: Session, provider: Provider) -> Provider:
    session.add(provider)
    session.commit()
    session.refresh(provider)
    return provider


def get_provider_by_id(session: Session, provider_id: int) -> Optional[Provider]:
    return session.get(Provider, provider_id)


def get_provider_by_name(session: Session, name: str) -> Optional[Provider]:
    statement = select(Provider).where(Provider.name == name)
    return session.exec(statement).first()


def get_or_create_provider_by_name(session: Session, name: str) -> Provider:
    provider = get_provider_by_name(session, name)
    if provider:
        return provider
    return create_provider(session, Provider(name=name))


def list_providers(
    session: Session,
    *,
    country: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Provider]:
    statement = select(Provider)
    if country:
        statement = statement.where(Provider.country == country)
    if tag:
        statement = statement.where(Provider.tags.contains([tag]))
    if q:
        like = f"%{q}%"
        statement = statement.where(Provider.name.ilike(like) | Provider.description.ilike(like))
    statement = statement.limit(limit).offset(offset)
    return session.exec(statement).all()


# Product CRUD / search

def create_product(session: Session, product: Product) -> Product:
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def get_product_by_url(session: Session, url: str) -> Optional[Product]:
    statement = select(Product).where(Product.url == url)
    return session.exec(statement).first()


def list_products(
    session: Session,
    *,
    provider_id: Optional[int] = None,
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    tag: Optional[str] = None,
    skin_type: Optional[str] = None,
    ingredient: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Product]:
    statement = select(Product)
    if provider_id is not None:
        statement = statement.where(Product.provider_id == provider_id)
    if q:
        like = f"%{q}%"
        statement = statement.where(Product.name.ilike(like) | Product.description.ilike(like))
    if min_price is not None:
        statement = statement.where(Product.price_amount >= min_price)
    if max_price is not None:
        statement = statement.where(Product.price_amount <= max_price)
    if tag:
        statement = statement.where(Product.tags.contains([tag]))
    if skin_type:
        statement = statement.where(Product.skin_types.contains([skin_type]))
    if ingredient:
        statement = statement.where(Product.inci.contains([ingredient]))
    statement = statement.limit(limit).offset(offset)
    return session.exec(statement).all() 