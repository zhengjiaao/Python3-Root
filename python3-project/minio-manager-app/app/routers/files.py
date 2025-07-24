from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from ..dependencies import get_minio
from ..utils.minio_client import MinioClient
from starlette.responses import StreamingResponse

router = APIRouter()


@router.post("/upload")
async def upload_file(
        file: UploadFile = File(...),
        minio: MinioClient = Depends(get_minio)
):
    if minio.upload_file(file, file.filename):
        return {"message": f"File {file.filename} uploaded successfully"}
    raise HTTPException(500, "File upload failed")


@router.get("/download/{file_name}")
async def download_file(
        file_name: str,
        minio: MinioClient = Depends(get_minio)
):
    file = minio.download_file(file_name)
    if not file:
        raise HTTPException(404, "File not found")

    return StreamingResponse(
        file.stream(32 * 1024),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )


@router.delete("/delete/{file_name}")
async def delete_file(
        file_name: str,
        minio: MinioClient = Depends(get_minio)
):
    if minio.delete_file(file_name):
        return {"message": f"File {file_name} deleted successfully"}
    raise HTTPException(500, "File deletion failed")