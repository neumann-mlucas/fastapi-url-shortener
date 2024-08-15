from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import UrlModel, UrlRegister
from app.utils.hash import from_hash, to_hash


class UrlRepository:
    "CRUD absctrciton over the SQL table"

    def get(self, hash: str, db: Session) -> UrlModel | None:
        record = db.get(UrlRegister, from_hash(hash))
        if record is None:
            return None
        return UrlModel(hash=to_hash(record.idx), url=record.url)

    def get_by_url(self, url: str, db: Session) -> UrlModel | None:
        stmt = select(UrlRegister).where(UrlRegister.url == url)
        record = db.execute(stmt).scalars().first()
        if record is None:
            return None
        return UrlModel(hash=to_hash(record.idx), url=record.url)

    def get_all(self, db: Session) -> list[UrlModel]:
        stmt = select(UrlRegister)
        records = db.execute(stmt).scalars().all()
        return [
            UrlModel(hash=to_hash(record.idx), url=record.url) for record in records
        ]

    def add(self, url: str, db: Session) -> UrlModel | None:
        record = UrlRegister(url=url)

        try:
            db.add(record)
            db.commit()
        except IntegrityError:
            db.rollback()
            return None  # handle duplicate url case

        return UrlModel(hash=to_hash(record.idx), url=record.url)

    def delete(self, hash: str, db: Session) -> UrlModel | None:
        record = db.get(UrlRegister, from_hash(hash))
        if record is None:
            return None
        db.delete(record)
        db.commit()
        return UrlModel(hash=to_hash(record.idx), url=record.url)


url_repository = UrlRepository()
