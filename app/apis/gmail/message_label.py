from typing import List, Union

from fastapi import APIRouter, status, Depends

from app.lib.exception_handler import error_handler
from app.lib.pydantic_helper import make_dependable
from app.schema_models import ListRequest, GetByMessageIdRequest, MessageLabelResponse
from app.schema_models import SearchRequest, GetByLabelIdRequest
from app.services import MessageLabelService

message_label_router = APIRouter()


@message_label_router.get(
	"/list", response_model=Union[List[MessageLabelResponse], int],
	status_code=status.HTTP_200_OK, tags=["Message Label APIs"],
	summary="Get all message labels"
)
@error_handler
async def get_all_message_labels(query_params: ListRequest = Depends(make_dependable(ListRequest))):
	"""
	Get all message labels. This API will return all the message labels in the system.
	"""
	labels = MessageLabelService().get_all_message_labels(query_params)

	return labels


@message_label_router.get(
	"/get_by_label_id/{label_id}", response_model=Union[List[MessageLabelResponse], MessageLabelResponse],
	status_code=status.HTTP_200_OK, tags=["Message Label APIs"],
	summary="Get label details by label id"
)
@error_handler
async def get_message_label_by_label_id(path_params: GetByLabelIdRequest = Depends()):
	"""
	Get message label by label id. This API will return the message labels for the given label id.
	"""
	label = MessageLabelService().get_label_by_label_id(path_params.label_id)

	return label


@message_label_router.get(
	"/get_by_message_id/{message_id}", response_model=Union[List[MessageLabelResponse], MessageLabelResponse],
	status_code=status.HTTP_200_OK, tags=["Message Label APIs"],
	summary="Get label details by label name"
)
@error_handler
async def get_message_label_by_message_id(path_params: GetByMessageIdRequest = Depends()):
	"""
	Get message label by label name. This API will return the message label for the given message id.
	"""
	label = MessageLabelService().get_label_by_message_id(path_params.message_id)

	return label


@message_label_router.get(
	"/search", response_model=Union[List[MessageLabelResponse], int],
	status_code=status.HTTP_200_OK, tags=["Message Label APIs"],
	summary="Search labels"
)
@error_handler
async def search_label(query_params: SearchRequest = Depends(make_dependable(SearchRequest))):
	"""
	Search message labels. This API will return the message labels based on the search criteria.
	The API supports partial search as well.
	"""
	label = MessageLabelService().search_message_label(query_params)

	return label
