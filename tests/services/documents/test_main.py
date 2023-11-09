def test_health_check(http_client):
    """Verify that the health check route behaves"""
    # Act
    response = http_client.get("/health-check")

    # Assert
    assert response.status_code == 200, response.json()
    assert response.text == '"OK"'
