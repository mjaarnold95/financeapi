import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.imports import ImportSummary
from app.services.csv_import import import_csv_bytes

router = APIRouter()

@router.post("/csv", response_model=ImportSummary, status_code=201)
async def import_csv(
    account_id: uuid.UUID = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        # still accept, but warn by requiring csv content-type? keep simple
        pass

    content = await file.read()
    try:
        job, stats = import_csv_bytes(db, account_id=account_id, filename=file.filename, content=content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return {
        "job": job,
        "total_rows": stats["total_rows"],
        "created": stats["created"],
        "skipped_duplicates": stats["skipped_duplicates"],
        "categorized": stats["categorized"],
    }
