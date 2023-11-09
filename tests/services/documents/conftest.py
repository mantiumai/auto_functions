import pytest

from auto_functions.services.documents.main import app


@pytest.fixture
def http_client(create_http_client):
    """Return a default HTTP client"""
    return create_http_client(app)
