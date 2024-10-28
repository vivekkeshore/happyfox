from typing import List, Union

from fastapi import APIRouter, status, Depends

from app.lib.exception_handler import error_handler
from app.lib.pydantic_helper import make_dependable
from app.schema_models import GetByMessageIdRequest, SearchRequest
from app.schema_models import MessageBodyResponse
from app.services import MessageBodyService

message_body_router = APIRouter()


@message_body_router.get(
	"/get_by_message_id/{message_id}", response_model=MessageBodyResponse,
	status_code=status.HTTP_200_OK, tags=["Message Body APIs"],
	summary="Get message body by message id"
)
@error_handler
async def get_message_body_by_message_id(path_params: GetByMessageIdRequest = Depends()):
	"""
	Get message body by message id. This API will return the message body for the given message id.
	"""
	message = MessageBodyService().get_message_body_by_message_id(path_params.message_id)

	return message


@message_body_router.get(
	"/search", response_model=Union[List[MessageBodyResponse], int],
	status_code=status.HTTP_200_OK, tags=["Message Body APIs"],
	summary="Search messages body"
)
@error_handler
async def search_message(query_params: SearchRequest = Depends(make_dependable(SearchRequest))):
	"""
	Search messages body. This API will return the messages body based on the search criteria.
	The API supports partial search as well.
	"""
	message = MessageBodyService().search_message_body(query_params)

	return message
