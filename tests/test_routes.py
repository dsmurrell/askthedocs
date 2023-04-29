from fastapi.testclient import TestClient

from main import app

test_client = TestClient(app)


def test_hello_world_route():
    response = test_client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
