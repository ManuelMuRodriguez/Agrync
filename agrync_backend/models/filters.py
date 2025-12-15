
from enum import Enum
from pydantic import BaseModel
from typing import Any




class FilterMode(str, Enum):
    contains = 'contains'
    startsWith = 'startsWith'
    endsWith = 'endsWith'

class ColumnFilter(BaseModel):
    id: str
    value: Any

class Pagination(BaseModel):
    pageIndex: int = 0
    pageSize: int = 10

class FiltersPayload(BaseModel):
    pagination: Pagination
    columnFilters: list[ColumnFilter] = []
    columnFilterFns: dict[str, str] = {}
    sorting: list[dict[str, Any]] = []
    globalFilter: str | None = None