from typing import Optional

from fastapi import Query, Path
from pydantic import BaseModel, Field, Extra, model_validator

from app.lib.constants import UUID_REGEX


class BaseRequest(BaseModel, extra=Extra.forbid):
	id: str = Field(..., pattern=UUID_REGEX, description="ID of the record.")


class GetByNameRequest(BaseModel, extra=Extra.forbid):
	name: str = Path(
		..., max_length=256, min_length=1, examples=["foobar"]
	)


class GetByIdRequest(BaseModel, extra=Extra.forbid):
	id: str = Path(..., pattern=UUID_REGEX, description="ID of the record.")


class ListRequest(BaseModel, extra=Extra.forbid):
	page: Optional[int] = Query(None, ge=1, description="Page Number", example=1)
	per_page: Optional[int] = Query(None, ge=1, description="Number of records per page", example=10)
	count: Optional[bool] = Query(
		False,
		description="Flag to count the number of records instead of returning the list",
		example=False
	)

	@model_validator(mode="before")
	def check_query_params(self):
		page, per_page, count = self.get('page'), self.get('per_page'), self.get('count')
		if (page or per_page) and count:
			raise ValueError('Cannot pass both count and page/per_page query params.')

		if (page or per_page) and not (page and per_page):
			raise ValueError('Both page and per_page params required for pagination.')

		return self


class ListRequestWithIsActive(ListRequest, extra=Extra.forbid):
	is_active: Optional[bool] = Query(
		None,
		description="Flag to get only active records",
		examples=[True, False]
	)


class SearchRequest(ListRequest):
	col: str = Query(
		..., min_length=1, max_length=20,
		description="Column name to filter the records.",
		example="name"
	)
	value: str = Query(
		..., min_length=1, max_length=256,
		description="Column value for column name to filter the records.",
		example="foobar"
	)


class SearchRequestWithIsActive(ListRequestWithIsActive):
	col: str = Query(
		..., min_length=1, max_length=20,
		description="Column name to filter the records.",
		example="name"
	)
	value: str = Query(
		..., min_length=1, max_length=256,
		description="Column value for column name to filter the records.",
		example="foobar"
	)
