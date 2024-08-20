from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UrlModel, UrlRegister
from app.utils.hash import from_hash, to_hash


def _to_model(item: UrlRegister) -> UrlModel:
    "helper function to convert a database row model to a pydantic obj"
    return UrlModel(hash=to_hash(item.idx), url=item.url, on=item.on)


class UrlRepository:
    "CRUD abstraction over the SQL table"

    async def get(self, hash: str, db: AsyncSession) -> UrlModel | None:
        """Retrieve a URL record by its hash."""
        item = await db.get(UrlRegister, from_hash(hash))
        return _to_model(item) if item else None

    async def get_by_url(self, url: str, db: AsyncSession) -> UrlModel | None:
        """Retrieve a URL record by its URL."""
        stmt = select(UrlRegister).where(UrlRegister.url == url)
        item = (await db.execute(stmt)).scalars().first()
        return _to_model(item) if item else None

    async def get_all(self, db: AsyncSession) -> list[UrlModel]:
        """Retrieve all URL records."""
        stmt = select(UrlRegister)
        items = (await db.execute(stmt)).scalars().all()
        return [_to_model(item) for item in items]

    async def add(self, url: str, db: AsyncSession) -> UrlModel | None:
        """Add a new URL record."""
        item = UrlRegister(url=url)

        try:
            db.add(item)
            await db.commit()
            await db.refresh(item)
            return _to_model(item)
        except IntegrityError:  # handle duplicate URL case
            await db.rollback()
            return None

    async def delete(self, hash: str, db: AsyncSession) -> UrlModel | None:
        """Delete a URL record by its hash."""
        item = await db.get(UrlRegister, from_hash(hash))
        if item is None:
            return None
        await db.delete(item)
        await db.commit()
        return _to_model(item)

    async def update(self, update: UrlModel, db: AsyncSession) -> UrlModel | None:
        """Update an existing URL record."""
        item = await db.get(UrlRegister, from_hash(update.hash))
        if item is None:
            return None

        # update fields only if they are provided
        if update.url is not None:
            item.url = str(update.url)
        if update.on is not None:
            item.on = update.on

        await db.commit()
        await db.refresh(item)
        return _to_model(item)


url_repository = UrlRepository()
