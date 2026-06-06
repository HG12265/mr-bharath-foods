from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.repositories.base import BaseRepository

T = TypeVar("T", bound=BaseModel)

class BaseService(Generic[T]):
    def __init__(self, repository: BaseRepository[T]):
        self.repository = repository

    async def get_by_id(self, id_str: str) -> T | None:
        return await self.repository.get_by_id(id_str)

    async def list_records(self, filter_query: dict[str, Any], skip: int = 0, limit: int = 100) -> list[T]:
        return await self.repository.find(filter_query, skip=skip, limit=limit)

    async def create_record(self, data: BaseModel) -> T:
        return await self.repository.insert(data)

    async def update_record(self, id_str: str, update_data: dict[str, Any]) -> T | None:
        return await self.repository.update(id_str, update_data)

    async def remove_record_soft(self, id_str: str) -> bool:
        return await self.repository.soft_delete(id_str)

    async def remove_record_hard(self, id_str: str) -> bool:
        return await self.repository.delete(id_str)
