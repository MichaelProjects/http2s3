import os
import logging

from fastapi import Response, status, APIRouter, status, Depends
from fastapi import FastAPI, UploadFile, HTTPException
from app.lib.other import encrypt_message

from app.lib.s3 import upload_object


v1_router = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)


@v1_router.post("/{bucket}/{filename}")
async def upload_ressource(bucket: str, filename: str, response: Response, file: UploadFile = None):
    if not file:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail":"File not provided"}

    if not "." in filename:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"detail":"Filename must contain a file extension"}
    
    try: 
        contents = await file.read()
        if os.environ["encryption_on"].lower() == "true":
            contents = encrypt_message(contents, os.environ["encryption_key"])
        res = await upload_object(file=contents, filename=filename, bucket=bucket)
        
        # if upload was not successful
        if not isinstance(res, str):
            raise Exception()
        
        return {"filename": file.filename, "content_length": len(contents)}
    except Exception as e:
        logging.error(f"Failed to upload file: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"detail":"Failed to read file or upload file"}
