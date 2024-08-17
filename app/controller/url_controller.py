from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import UrlModel
from app.repository.url_repository import url_repository


class UrlRequest(BaseModel):
    url: HttpUrl


class UrlResponse(BaseModel):
    data: UrlModel
    status: str = "success"
    errors: str | None = None


class MultipleUrlsResponse(BaseModel):
    data: list[UrlModel]
    status: str = "success"
    errors: str | None = None


router = APIRouter(prefix="/api/v1", tags=["UrlShortener API"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{hash}", response_model=UrlResponse)
def get(hash: str, db: Session = Depends(get_db)):
    record = url_repository.get(hash, db)
    if record is None:
        raise HTTPException(status_code=404, detail="url not found")
    return UrlResponse(data=record)


@router.get("/", response_model=MultipleUrlsResponse)
def get_all(db: Session = Depends(get_db)):
    records = url_repository.get_all(db)
    if records is None or not len(records):
        raise HTTPException(status_code=404, detail="no register found in db")
    return MultipleUrlsResponse(data=records)


@router.post("/", response_model=UrlResponse)
def create(data: UrlRequest, db: Session = Depends(get_db)):
    record = url_repository.add(str(data.url), db)
    if record:
        return UrlResponse(data=record)

    # case where url already in database
    record = url_repository.get_by_url(str(data.url), db)
    if record is None:  # race condition with delete?
        raise HTTPException(status_code=404, detail="record was deleted, try again")

    return UrlResponse(data=record, status="warning", errors="url already in db")


@router.delete("/{hash}", response_model=UrlResponse)
def delete(hash: str, db: Session = Depends(get_db)):
    record = url_repository.delete(hash, db)
    if record is None:
        raise HTTPException(status_code=404, detail="no register found in db")
    return UrlResponse(data=record)


@router.put("/{hash}", response_model=UrlResponse)
def update(hash: str, data: UrlRequest, db: Session = Depends(get_db)):
    record = url_repository.update(UrlModel(hash=hash, url=str(data.url), on=None), db)
    if record is None:
        raise HTTPException(status_code=404, detail="no register found in db")
    return UrlResponse(data=record)


@router.put("/activate/{hash}", response_model=UrlResponse)
def activate(hash: str, db: Session = Depends(get_db)):
    record = url_repository.update(UrlModel(hash=hash, url=None, on=True), db)
    if record is None:
        raise HTTPException(status_code=404, detail="no register found in db")
    return UrlResponse(data=record)


@router.put("/deactivate/{hash}", response_model=UrlResponse)
def deactivate(hash: str, db: Session = Depends(get_db)):
    record = url_repository.update(UrlModel(hash=hash, url=None, on=False), db)
    if record is None:
        raise HTTPException(status_code=404, detail="no register found in db")
    return UrlResponse(data=record)
