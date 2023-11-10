from typing import Any

from pydantic import BaseModel, Field
from pydantic.types import UUID4


class ApiSpecCreateParams(BaseModel):
    name: str
    spec: dict[str, Any] = Field(default={}, json_schema_extra=dict(no_db=True))


class ApiSpec(BaseModel):
    id: UUID4
    name: str
    assistant_file_id: str
