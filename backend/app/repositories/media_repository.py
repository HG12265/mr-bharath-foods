from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import COLLECTION_MEDIA_ASSETS
from app.models.media_asset import MediaAsset
from app.repositories.base import BaseRepository


class MediaRepository(BaseRepository[MediaAsset]):
    def __init__(self, db: AsyncDatabase):  # type: ignore[type-arg]
        super().__init__(db, COLLECTION_MEDIA_ASSETS, MediaAsset)
