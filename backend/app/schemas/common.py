from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total_docs: int
    total_pages: int
    has_next: bool
    has_prev: bool

class Envelope(BaseModel, Generic[T]):
    success: bool = True
    message: str | None = None
    data: T | None = None
    meta: PaginationMeta | None = None

class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None

class ErrorEnvelope(BaseModel):
    success: bool = False
    message: str
    errors: list[ErrorDetail] = []
