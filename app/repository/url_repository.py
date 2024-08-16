from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import UrlModel, UrlRegister
from app.utils.hash import from_hash, to_hash


class UrlRepository:
    "CRUD absctrciton over the SQL table"

    def get(self, hash: str, db: Session) -> UrlModel | None:
        item = db.get(UrlRegister, from_hash(hash))
        if item is None:
            return None
        return UrlModel(hash=to_hash(item.idx), url=item.url, on=item.on)

    def get_by_url(self, url: str, db: Session) -> UrlModel | None:
        stmt = select(UrlRegister).where(UrlRegister.url == url)
        item = db.execute(stmt).scalars().first()
        if item is None:
            return None
        return UrlModel(hash=to_hash(item.idx), url=item.url, on=item.on)

    def get_all(self, db: Session) -> list[UrlModel]:
        stmt = select(UrlRegister)
        items = db.execute(stmt).scalars().all()
        return [
            UrlModel(hash=to_hash(item.idx), url=item.url, on=item.on) for item in items
        ]

    def add(self, url: str, db: Session) -> UrlModel | None:
        item = UrlRegister(url=url)

        try:
            db.add(item)
            db.commit()
        except IntegrityError:
            db.rollback()
            return None  # handle duplicate url case

        return UrlModel(hash=to_hash(item.idx), url=item.url, on=item.on)

    def delete(self, hash: str, db: Session) -> UrlModel | None:
        item = db.get(UrlRegister, from_hash(hash))
        if item is None:
            return None
        db.delete(item)
        db.commit()
        return UrlModel(hash=to_hash(item.idx), url=item.url, on=item.on)

    def update(self, update: UrlModel, db: Session) -> UrlModel | None:
        item = db.get(UrlRegister, from_hash(update.hash))
        if item is None:
            return None

        # update fields only if they are provided

        if update.url is not None:
            item.url = str(update.url)

        if update.on is not None:
            item.on = update.on

        db.commit()
        db.refresh(item)
        return UrlModel(hash=to_hash(item.idx), url=item.url, on=item.on)


url_repository = UrlRepository()
