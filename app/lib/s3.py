import os
from typing import BinaryIO, Union

import aioboto3
import logging


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


async def check_for_object(filename: str) -> bool:
    session = aioboto3.Session()
    async with session.resource("s3", endpoint_url=os.environ["cluster_url"], aws_access_key_id=os.environ["api_key"], aws_secret_access_key=os.environ["secret_key"]) as s3:
        try:
            y = await s3.Object(os.environ["bucket"], filename)
            return True
        except Exception as e:
            logging.error(f"Faild to check for object: {e}")
            return False