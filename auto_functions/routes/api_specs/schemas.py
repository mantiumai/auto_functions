from typing import Any

from pydantic import BaseModel
from pydantic.types import UUID4


class ApiSpecCreateParams(BaseModel):
    name: str
    spec: dict[str, Any]


class ApiSpec(ApiSpecCreateParams):
    id: UUID4
