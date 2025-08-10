from __future__ import annotations
from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy import JSON, Column


class Provider(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    website: Optional[str] = Field(default=None, index=True)
    country: Optional[str] = Field(default=None, index=True)
    description: Optional[str] = None
    pros: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    cons: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    tags: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider_id: int = Field(index=True, foreign_key="provider.id")
    name: str = Field(index=True)
    url: Optional[str] = Field(default=None, index=True)
    description: Optional[str] = None

    price_amount: Optional[float] = Field(default=None, index=True)
    price_currency: Optional[str] = Field(default="SEK", index=True)

    ingredients: Optional[str] = None
    inci: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    tags: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    skin_types: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    pros: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))
    cons: Optional[list[str]] = Field(default=None, sa_column=Column(JSON))

    rating: Optional[float] = Field(default=None, index=True) 