from fastapi.testclient import TestClient

from renkon.web.app import app


def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
