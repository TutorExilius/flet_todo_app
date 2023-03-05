from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, constr  # pylint: disable=no-name-in-module

StripWhitespaces: constr = constr(strip_whitespace=True)


class TaskModel(BaseModel):  # pylint: disable=too-few-public-methods
    name: StripWhitespaces
    completed: bool = False
    task_id: UUID | None = None

    def __init__(self, **data: Any):
        super().__init__(**data)

        if self.task_id is None:
            self.task_id = uuid4()
