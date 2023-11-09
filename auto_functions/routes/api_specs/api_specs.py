from typing import Mapping
from uuid import uuid4

from fastapi import APIRouter, status
from pydantic import UUID4

from auto_functions.routes.api_specs.schemas import ApiSpec, ApiSpecCreateParams

api_specs: Mapping[UUID4, ApiSpec] = {}

api_spec_router = APIRouter(prefix="/api-specs")


@api_spec_router.post(
    "/",
    summary="Create an API spec",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiSpec,
)
def create_api_spec(api_spec: ApiSpecCreateParams):
    api_spec = ApiSpec(**api_spec.model_dump(), id=uuid4())
    global api_specs
    api_specs[api_spec.id] = api_spec
    return api_spec


@api_spec_router.get(
    "/",
    summary="List API specs",
    response_model=list[ApiSpec],
)
def list_api_specs():
    global api_specs
    return list(api_specs.values())
