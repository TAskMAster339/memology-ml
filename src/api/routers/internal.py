import os
import shutil
from pathlib import Path

from fastapi import APIRouter, File, Header, HTTPException, UploadFile, status

from src.config.settings import ConfigManager

router = APIRouter(prefix="/internal", tags=["Internal"], include_in_schema=False)

config_manager = ConfigManager()
app_config = config_manager.load_config()

WORKER_SECRET_TOKEN = os.getenv("WORKER_SECRET_TOKEN")
UPLOAD_DIR = Path(app_config.output_dir)


@router.post("/upload/{task_id}", status_code=status.HTTP_201_CREATED)
async def upload_meme_result(
    task_id: str,
    file: UploadFile = File(...),
    x_worker_token: str | None = Header(None),
):
    """Принимает сгенерированное изображение от воркера."""
    if x_worker_token != WORKER_SECRET_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid worker token")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / file.filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        await file.close()

    return {"filename": file_path.name, "task_id": task_id, "size": file.size, "path_on_server": str(file_path)}