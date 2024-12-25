import os
import logging
from typing import BinaryIO, Union

from fastapi import Response, status, APIRouter, status, Depends
from fastapi import FastAPI, UploadFile, HTTPException, Header
from fastapi.responses import StreamingResponse
from app.lib.other import encrypt_message, decrypt_message
from cryptography.fernet import Fernet, InvalidToken
import base64
import aioboto3
from typing import AsyncGenerator

CHUNK_SIZE = 100 * 1024 * 1024


async def upload_object(file: BinaryIO, filename: str, bucket: str) -> Union[str, bool]:
    session = aioboto3.Session()
    async with session.resource("s3", endpoint_url=os.environ["cluster_url"], aws_access_key_id=os.environ["api_key"], aws_secret_access_key=os.environ["secret_key"]) as s3:
        try:
            bucket = await s3.Bucket(bucket)
            y = await bucket.put_object(Key=filename, Body=file)
            return os.environ["cluster_url"] + "/" + filename
        except Exception as e:
            logging.error(f"Faild to upload object: {e}")
            return False


async def stream_file_to_s3(file: UploadFile, bucket: str, filename: str):
    """
    Function is used to stream files using multipart request to s3.
    """
    session = aioboto3.Session()
    async with session.client("s3", endpoint_url=os.environ["cluster_url"],
                               aws_access_key_id=os.environ["api_key"],
                               aws_secret_access_key=os.environ["secret_key"]) as s3:
        multipart_upload = await s3.create_multipart_upload(Bucket=bucket, Key=filename)
        upload_id = multipart_upload['UploadId']

        try:
            part_number = 1
            parts = []

            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break

                if os.environ["encryption_on"].lower() == "true":
                    chunk = encrypt_message(chunk, os.environ["encryption_key"])

                part = await s3.upload_part(Bucket=bucket, Key=filename, PartNumber=part_number,
                                            UploadId=upload_id, Body=chunk)
                parts.append({"PartNumber": part_number, "ETag": part["ETag"]})
                part_number += 1

            await s3.complete_multipart_upload(Bucket=bucket, Key=filename, UploadId=upload_id,
                                               MultipartUpload={"Parts": parts})

            return os.environ["cluster_url"] + "/" + filename
        except Exception as e:
            logging.error(f"Failed to upload file: {e}")
            await s3.abort_multipart_upload(Bucket=bucket, Key=filename, UploadId=upload_id)
            raise

async def check_for_object(filename: str) -> bool:
    session = aioboto3.Session()
    async with session.resource("s3", endpoint_url=os.environ["cluster_url"], aws_access_key_id=os.environ["api_key"], aws_secret_access_key=os.environ["secret_key"]) as s3:
        try:
            y = await s3.Object(os.environ["bucket"], filename)
            return True
        except Exception as e:
            logging.error(f"Faild to check for object: {e}")
            return False

async def get_s3_object_stream(file_path: str, filename: str):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=os.environ["cluster_url"],
        aws_access_key_id=os.environ["api_key"],
        aws_secret_access_key=os.environ["secret_key"]
    ) as s3:
        try:
            response = await s3.get_object(Bucket=file_path, Key=filename)
            return response["Body"]
        except Exception as e:
            logging.error(f"Failed to get object from S3: {e}")
            raise Exception("File not found")


async def retrieve_s3_object_stream(file_path: str, filename: str):
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url=os.environ["cluster_url"],
        aws_access_key_id=os.environ["api_key"],
        aws_secret_access_key=os.environ["secret_key"]
    ) as s3:
        try:
            response = await s3.get_object(Bucket=file_path, Key=filename)
            try:
                buffer = b""
                chunk_count = 0
                async for chunk in response["Body"].iter_chunks():
                    chunk_count += 1
                    logging.debug(f"Received chunk {chunk_count}: {len(chunk)} bytes")
                    buffer += chunk
                    while len(buffer) >= CHUNK_SIZE:
                        try:
                            decrypted_chunk = decrypt_message(buffer[:CHUNK_SIZE], os.environ["encryption_key"])
                            logging.error(f"Decrypted chunk: {len(decrypted_chunk)} bytes")
                            yield decrypted_chunk
                            buffer = buffer[CHUNK_SIZE:]
                        except InvalidToken:
                            logging.error(f"Invalid token encountered, yielding raw chunk")
                            yield buffer[:CHUNK_SIZE]
                            buffer = buffer[CHUNK_SIZE:]

                logging.debug(f"Finished streaming. Total chunks: {chunk_count}")

                # Process any remaining data in the buffer
                if buffer:
                    logging.debug(f"Processing remaining buffer: {len(buffer)} bytes")
                    try:
                        yield decrypt_message(buffer, os.environ["encryption_key"])
                    except InvalidToken:
                        logging.warning(f"Invalid token encountered in remaining buffer")
                        yield buffer
            except Exception as e:
                logging.error(f"Error in decrypt_and_stream: {e}")
                raise
        except Exception as e:
            logging.error(f"Failed to get object from S3: {e}")
            raise Exception("File not found")

async def delete_object(file_path: str, filename: str):
    session = aioboto3.Session()
    async with session.resource("s3", endpoint_url=os.environ["cluster_url"], aws_access_key_id=os.environ["api_key"], aws_secret_access_key=os.environ["secret_key"]) as s3:
        try:
            y = await s3.Object(file_path, filename)
            res = await y.delete()
            logging.debug(res)
        except Exception as e:
            logging.error(f"Failed to get object from S3: {e}")
            raise Exception("File not found")