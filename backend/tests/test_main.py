def test_health_endpoint_returns_200_and_ok(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_headers_present_on_success(client):
    response = client.get(
        "/api/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_headers_present_on_error(client):
    response = client.get(
        "/api/nonexistent",
        headers={"Origin": "http://localhost:5173"},
    )
    assert response.status_code == 404
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_app_boots_with_lifespan(client):
    assert client.get("/api/health").status_code == 200
