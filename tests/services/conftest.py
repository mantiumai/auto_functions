import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from auto_functions.services.main import app


@pytest.fixture
def create_http_client():
    """Return a function that creates a HTTP client"""

    def _create(app: FastAPI) -> TestClient:
        return TestClient(app, base_url="https://testserver")

    yield _create


@pytest.fixture
def http_client(create_http_client):
    """Return a default HTTP client"""
    return create_http_client(app)
