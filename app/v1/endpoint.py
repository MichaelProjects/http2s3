import os
import logging

from fastapi import Response, status, APIRouter, status, Depends
from fastapi import FastAPI, UploadFile, HTTPException, Header
from fastapi.responses import StreamingResponse
from app.lib.other import encrypt_message
from app.lib.s3 import upload_object, get_s3_object_stream
from cryptography.fernet import Fernet, InvalidToken

import aioboto3
from typing import AsyncGenerator


v1_router = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)

@v1_router.get("/{file_path}/{filename}")
async def get_download_resource(file_path: str, filename: str):
    try:
        logging.debug(f"Starting download for {file_path}/{filename}")
        # s3_stream = await get_s3_object_stream(file_path=file_path, filename=filename)
        decryption_key = os.environ.get("encryption_key")
        if not decryption_key:
            logging.error("Decryption key is missing")
            raise HTTPException(status_code=500, detail="Decryption key is missing")

        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/octet-stream",
            "X-Content-Type-Options": "nosniff"
        }
        async def test():
            session = aioboto3.Session()
            async with session.client(
                "s3",
                endpoint_url=os.environ["cluster_url"],
                aws_access_key_id=os.environ["api_key"],
                aws_secret_access_key=os.environ["secret_key"]
            ) as s3:
                f = Fernet(decryption_key)
                try:
                    response = await s3.get_object(Bucket=file_path, Key=filename)
                    try:
                        buffer = b""
                        chunk_count = 0
                        async for chunk in response["Body"].iter_chunks():
                            chunk_count += 1
                            logging.debug(f"Received chunk {chunk_count}: {len(chunk)} bytes")
                            buffer += chunk
                            while len(buffer) >= 1024:  # Process in 1KB chunks
                                try:
                                    decrypted_chunk = f.decrypt(buffer[:1024])
                                    logging.debug(f"Decrypted chunk: {len(decrypted_chunk)} bytes")
                                    yield decrypted_chunk
                                    buffer = buffer[1024:]
                                except InvalidToken:
                                    logging.warning(f"Invalid token encountered, yielding raw chunk")
                                    yield buffer[:1024]
                                    buffer = buffer[1024:]

                        logging.debug(f"Finished streaming. Total chunks: {chunk_count}")

                        # Process any remaining data in the buffer
                        if buffer:
                            logging.debug(f"Processing remaining buffer: {len(buffer)} bytes")
                            try:
                                yield f.decrypt(buffer)
                            except InvalidToken:
                                logging.warning(f"Invalid token encountered in remaining buffer")
                                yield buffer
                    except Exception as e:
                        logging.error(f"Error in decrypt_and_stream: {e}")
                        raise
                except Exception as e:
                    logging.error(f"Failed to get object from S3: {e}")
                    raise Exception("File not found")

        return StreamingResponse(
            test(),
            headers=headers,
            media_type="text/event-stream"
        )
    except Exception as e:
        logging.error(f"Error in get_download_resource: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@v1_router.post("/{file_path}/{filename}")
async def upload_ressource(file_path: str, filename: str, response: Response, file: UploadFile = None):
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
        res = await upload_object(file=contents, filename=filename, bucket=file_path)

        # if upload was not successful
        if not isinstance(res, str):
            raise Exception()

        return {"filename": file.filename, "content_length": len(contents)}
    except Exception as e:
        logging.error(f"Failed to upload file: {e}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"detail":"Failed to read file or upload file"}
