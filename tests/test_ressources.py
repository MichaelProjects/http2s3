import httpx


TEST_ENDPOINT = "http://localhost:8777/api/v1"

def test_get_object():
    res = httpx.get(f"{TEST_ENDPOINT}/jenkins_artifcats/lazerguard-0.6.x")
    print(res)
    assert False