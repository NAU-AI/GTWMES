from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class VariableDto(BaseModel):
    key: str
    value: Optional[Any]

    model_config = ConfigDict(from_attributes=True)
