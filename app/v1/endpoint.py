import os
import logging

from fastapi import Response, status, APIRouter, status, Depends
from fastapi import FastAPI, UploadFile, HTTPException, Header
from fastapi.responses import StreamingResponse
from app.lib.other import encrypt_message, decrypt_message
from app.lib.s3 import upload_object, get_s3_object_stream, stream_file_to_s3, retrieve_s3_object_stream
from cryptography.fernet import Fernet, InvalidToken
import base64
import aioboto3
from typing import AsyncGenerator


v1_router = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)
# minimum of 100 mb
CHUNK_SIZE = 100 * 1024 * 1024

@v1_router.get("/{file_path}/{filename}")
async def get_download_resource(file_path: str, filename: str):
    try:
        logging.debug(f"Starting download for {file_path}/{filename}")
        decryption_key = os.environ.get("encryption_key")
        if not decryption_key:
            logging.error("Decryption key is missing")
            raise HTTPException(status_code=500, detail="Decryption key is missing")

        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/octet-stream",
            "X-Content-Type-Options": "nosniff"
        }

        return StreamingResponse(
            retrieve_s3_object_stream(file_path, filename),
            headers=headers,
            media_type="text/event-stream"
        )
    except Exception as e:
        logging.error(f"Error in get_download_resource: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@v1_router.post("/{file_path}/{filename}")
async def upload_resource(file_path: str, filename: str, response: Response, file: UploadFile = None):
    if not file:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail": "File not provided"}

    if "." not in filename:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail": "Filename must contain a file extension"}

    try:
        upload_url = await stream_file_to_s3(file, file_path, filename)
        return {"filename": filename, "upload_url": upload_url}
    except Exception as e:
        logging.error(f"Failed to upload file: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"detail": "Failed to upload file"}
