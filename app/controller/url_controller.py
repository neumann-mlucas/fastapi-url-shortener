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


router = APIRouter(prefix="/api/v1/urls", tags=["UrlShortener API"])


@router.get("/{hash}", response_model=UrlResponse)
async def get(hash: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a URL by its hash if it's active, using cache if available."""
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="Invalid short URL")

    rd = await get_redis()

    # check if short URL alreadt in cache
    if cached := await rd.get(hash):
        UrlResponse(data=UrlModel(url=cached, hash=hash, on=True))

    # query the SQL DB
    record = await url_repository.get(hash, db)
    if record is None or not record.on:
        raise HTTPException(status_code=404, detail="URL not found")

    # cache short URL
    await rd.set(record.hash, str(record.url))

    return UrlResponse(data=record)


@router.get("/", response_model=MultipleUrlsResponse)
async def get_all(db: AsyncSession = Depends(get_db)):
    """Retrieve all URL records."""
    records = await url_repository.get_all(db)
    if records is None or not len(records):
        raise HTTPException(status_code=404, detail="No URLs found")
    return MultipleUrlsResponse(data=records)


@router.post("/", response_model=UrlResponse)
async def create(data: UrlRequest, db: AsyncSession = Depends(get_db)):
    """Register a new short URL, or return the existing one if already registered."""
    rd = await get_redis()

    # try to add URL to database
    record = await url_repository.add(str(data.url), db)
    if record:
        await rd.set(record.hash, str(record.url))  # cache short URL
        return UrlResponse(data=record)

    # case where the URL is already in the DB
    existing_record = await url_repository.get_by_url(str(data.url), db)
    if existing_record is None:  # probalby not needed
        raise HTTPException(
            status_code=404, detail="Record was deleted or not found, try again"
        )

    # cache the old short url just to be sure
    await rd.set(existing_record.hash, str(existing_record.url))

    return UrlResponse(
        data=existing_record, status="warning", errors="URL already in database"
    )


@router.delete("/{hash}", response_model=UrlResponse)
async def delete(hash: str, db: AsyncSession = Depends(get_db)):
    """Delete a URL record by its hash."""
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="Invalid short URL")

    record = await url_repository.delete(hash, db)
    if record is None:
        raise HTTPException(status_code=404, detail="No record found to delete")

    # sync cache with db
    rd = await get_redis()
    await rd.delete(record.hash)

    return UrlResponse(data=record)


@router.put("/{hash}", response_model=UrlResponse)
async def update(hash: str, data: UrlRequest, db: AsyncSession = Depends(get_db)):
    """Update the URL of a given short URL."""
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="Invalid short URL")

    input = UrlModel(hash=hash, url=str(data.url), on=None)
    record = await url_repository.update(input, db)
    if record is None:
        raise HTTPException(status_code=404, detail="No record found to update")

    # sync cache with db
    rd = await get_redis()
    await rd.set(record.hash, str(record.url))

    return UrlResponse(data=record)


@router.put("/activate/{hash}", response_model=UrlResponse)
async def activate(hash: str, db: AsyncSession = Depends(get_db)):
    """Activate a short URL."""
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="Invalid short URL")

    record = await url_repository.update(UrlModel(hash=hash, url=None, on=True), db)
    if record is None:
        raise HTTPException(status_code=404, detail="No record found to activate")

    return UrlResponse(data=record)


@router.put("/deactivate/{hash}", response_model=UrlResponse)
async def deactivate(hash: str, db: AsyncSession = Depends(get_db)):
    """Deactivate a short URL."""
    if not valid_hash(hash):
        raise HTTPException(status_code=400, detail="Invalid short URL")

    record = await url_repository.update(UrlModel(hash=hash, url=None, on=False), db)
    if record is None:
        raise HTTPException(status_code=404, detail="No record found to deactivate")

    # sync cache with db
    rd = await get_redis()
    await rd.delete(record.hash)

    return UrlResponse(data=record)
