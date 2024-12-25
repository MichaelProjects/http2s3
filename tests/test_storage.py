import pytest

from app.lib.s3 import upload_object, delete_object


FILENAME = "test0101.txt"
@pytest.mark.asyncio
async def test_object_creation():
    data = []
    with open("tests/resouces/test.txt", "rb") as file:
        data = file.read()
    res = await upload_object(data, filename=FILENAME, bucket="projects")
    print(res)
    assert False

@pytest.mark.asyncio
async def test_object_deletion():
    res = await delete_object("projects", FILENAME)
    print(res)
    assert False

