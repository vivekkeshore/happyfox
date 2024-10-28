from typing import List, Union

from fastapi import APIRouter, status, Depends

from app.lib.exception_handler import error_handler
from app.lib.pydantic_helper import make_dependable
from app.schema_models import ListRequest, FilterFieldResponse, GetByIdRequest
from app.schema_models import SearchRequest
from app.services import FilterFieldService

filter_field_router = APIRouter()


@filter_field_router.get(
	"/list", response_model=Union[List[FilterFieldResponse], int],
	status_code=status.HTTP_200_OK, tags=["Filter Field APIs"],
	summary="Get all filter fields"
)
@error_handler
async def get_all_filter_fields(query_params: ListRequest = Depends(make_dependable(ListRequest))):
	"""
	Get all filter fields. This API will return all the filter fields in the system.
	"""
	filter_fields = FilterFieldService().get_all_filter_fields(query_params)

	return filter_fields


@filter_field_router.get(
	"/get_by_id/{id}", response_model=FilterFieldResponse,
	status_code=status.HTTP_200_OK, tags=["Filter Field APIs"],
	summary="Get filter field by filter field id"
)
@error_handler
async def get_filter_field_by_id(path_params: GetByIdRequest = Depends()):
	"""
	Get message attachment by message attachment uuid. This API will return the message attachment for the given message attachment uuid.
	"""
	filter_field = FilterFieldService().get_filter_field_by_id(path_params.id)

	return filter_field


@filter_field_router.get(
	"/search", response_model=Union[List[FilterFieldResponse], int],
	status_code=status.HTTP_200_OK, tags=["Filter Field APIs"],
	summary="Search filter fields"
)
@error_handler
async def search_filter_field(query_params: SearchRequest = Depends(make_dependable(SearchRequest))):
	"""
	Search filter fields. This API will search for the filter fields based on the search query.
	"""
	filter_field = FilterFieldService().search_filter_field(query_params)

	return filter_field
