from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, get_redis
from app.models import UrlModel
from app.repository.url_repository import url_repository
from app.utils.hash import valid_hash


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


@router.get("/{hash}", response_model=UrlResponse)
async def get(hash: str, db: AsyncSession = Depends(get_db)):
    "given a valid hash, returns the corresponding URL if it's active"
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="invalid short url")

    rd = await get_redis()
    if cached := await rd.get(hash):  # get cached short url
        UrlResponse(data=UrlModel(url=cached, hash=hash, on=True))

    record = await url_repository.get(hash, db)
    if record is None:
        raise HTTPException(status_code=404, detail="url not found")
    if not record.on:  # only return active short URL
        raise HTTPException(status_code=404, detail="url not found")

    await rd.set(record.hash, str(record.url))  # cache short url
    return UrlResponse(data=record)


@router.get("/", response_model=MultipleUrlsResponse)
async def get_all(db: AsyncSession = Depends(get_db)):
    "debugging route, returns all short URLs"
    records = await url_repository.get_all(db)
    if records is None or not len(records):
        raise HTTPException(status_code=404, detail="no register found in db")
    return MultipleUrlsResponse(data=records)


@router.post("/", response_model=UrlResponse)
async def create(data: UrlRequest, db: AsyncSession = Depends(get_db)):
    "register a new short URL. if URL is already register, returns the old link"
    record = await url_repository.add(str(data.url), db)
    if record:
        return UrlResponse(data=record)

    # case where URL already in database
    record = await url_repository.get_by_url(str(data.url), db)
    if record is None:  # race condition with delete?
        raise HTTPException(status_code=404, detail="record was deleted, try again")

    # cache the new url
    rd = await get_redis()
    await rd.set(record.hash, str(record.url))

    return UrlResponse(data=record, status="warning", errors="url already in db")


@router.delete("/{hash}", response_model=UrlResponse)
async def delete(hash: str, db: AsyncSession = Depends(get_db)):
    "dev route, deletes a short URL from the database"
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="invalid short url")

    record = await url_repository.delete(hash, db)
    if record is None:
        raise HTTPException(status_code=404, detail="no register found in db")

    # sync cache with db
    rd = await get_redis()
    await rd.delete(record.hash)

    return UrlResponse(data=record)


@router.put("/{hash}", response_model=UrlResponse)
async def update(hash: str, data: UrlRequest, db: AsyncSession = Depends(get_db)):
    "dev route, update the original URL of a given short URL"
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="invalid short url")

    input = UrlModel(hash=hash, url=str(data.url), on=None)
    record = await url_repository.update(input, db)
    if record is None:
        raise HTTPException(status_code=404, detail="no register found in db")

    # sync cache with db
    rd = await get_redis()
    await rd.set(record.hash, str(record.url))

    return UrlResponse(data=record)


@router.put("/activate/{hash}", response_model=UrlResponse)
async def activate(hash: str, db: AsyncSession = Depends(get_db)):
    "dev route, activates a short URL"
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="invalid short url")

    record = await url_repository.update(UrlModel(hash=hash, url=None, on=True), db)
    if record is None:
        raise HTTPException(status_code=404, detail="no register found in db")
    return UrlResponse(data=record)


@router.put("/deactivate/{hash}", response_model=UrlResponse)
async def deactivate(hash: str, db: AsyncSession = Depends(get_db)):
    "dev route, deactivates a short URL"
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="invalid short url")

    record = await url_repository.update(UrlModel(hash=hash, url=None, on=False), db)
    if record is None:
        raise HTTPException(status_code=404, detail="no register found in db")

    # sync cache with db
    rd = await get_redis()
    await rd.delete(record.hash)

    return UrlResponse(data=record)
