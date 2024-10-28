from typing import List, Union

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.lib.exception_handler import error_handler
from app.lib.pydantic_helper import make_dependable
from app.schema_models import BaseRequest, GetByNameRequest, ListRequestWithIsActive, GetByIdRequest
from app.schema_models import SearchRequestWithIsActive, LabelResponse, GetByLabelIdRequest
from app.services import LabelService

label_router = APIRouter()


@label_router.get(
	"/list", response_model=Union[List[LabelResponse], int],
	status_code=status.HTTP_200_OK, tags=["Label APIs"],
	summary="Get all labels"
)
@error_handler
async def get_all_labels(query_params: ListRequestWithIsActive = Depends(make_dependable(ListRequestWithIsActive))):
	"""
	Get all labels. This API will return all the labels in the system.
	"""
	labels = LabelService().get_all_labels(query_params)

	return labels


@label_router.get(
	"/get_by_label_id/{label_id}", response_model=LabelResponse,
	status_code=status.HTTP_200_OK, tags=["Label APIs"],
	summary="Get label details by label id"
)
@error_handler
async def get_label_by_label_id(path_params: GetByLabelIdRequest = Depends()):
	"""
	Get label details by label id. This API will return the label details for the given label id.
	"""
	label = LabelService().get_label_by_label_id(path_params.label_id)

	return label


@label_router.get(
	"/get_by_name/{name}", response_model=LabelResponse,
	status_code=status.HTTP_200_OK, tags=["Label APIs"],
	summary="Get label details by label name"
)
@error_handler
async def get_label_by_name(path_params: GetByNameRequest = Depends()):
	"""
	Get label details by label name. This API will return the label details for the given label name.
	"""
	label = LabelService().get_label_by_name(path_params.name)

	return label


@label_router.get(
	"/get_by_id/{id}", response_model=LabelResponse,
	status_code=status.HTTP_200_OK, tags=["Label APIs"],
	summary="Get label details by label uuid"
)
@error_handler
async def get_label_by_id(path_params: GetByIdRequest = Depends()):
	"""
	Get label details by label uuid. This API will return the label details for the given label uuid.
	"""
	label = LabelService().get_label_by_id(path_params.id)

	return label


@label_router.get(
	"/search", response_model=Union[List[LabelResponse], int],
	status_code=status.HTTP_200_OK, tags=["Label APIs"],
	summary="Search labels"
)
@error_handler
async def search_label(query_params: SearchRequestWithIsActive = Depends(make_dependable(SearchRequestWithIsActive))):
	"""
	Search labels. This API will return the labels based on the search criteria.
	The API supports partial search as well.
	"""
	label = LabelService().search_label(query_params)

	return label


@label_router.put(
	"/deactivate",
	status_code=status.HTTP_200_OK, tags=["Label APIs"],
	summary="Soft delete the label"
)
@error_handler
async def deactivate_label(request: BaseRequest):
	"""
	Deactivate label. This API will deactivate the label or mark as inactive for the given label uuid (mandatory).
	"""
	LabelService().deactivate_label(request.id)

	return JSONResponse(
		content={"status": "success", "message": "Label deactivated successfully."},
		status_code=status.HTTP_200_OK
	)


@label_router.put(
	"/activate",
	status_code=status.HTTP_200_OK, tags=["Label APIs"],
	summary="Activate the label from deactivated stage. Equivalent to restoring from bin."
)
@error_handler
async def activate_label(request: BaseRequest):
	"""
	Activate label. This API will activate the label or mark as active for the given label uuid (mandatory).
	"""
	LabelService().activate_label(request.id)

	return JSONResponse(
		content={"status": "success", "message": "Label activated successfully."},
		status_code=status.HTTP_200_OK
	)
