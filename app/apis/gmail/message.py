from typing import List, Union

from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse

from app.lib.exception_handler import error_handler
from app.lib.pydantic_helper import make_dependable
from app.schema_models import BaseRequest, GetByMessageIdRequest, ListRequestWithIsActive, GetByIdRequest
from app.schema_models import SearchRequestWithIsActive, MessageResponse
from app.services import MessageService

message_router = APIRouter()


@message_router.get(
	"/list", response_model=Union[List[MessageResponse], int],
	status_code=status.HTTP_200_OK, tags=["Message APIs"],
	summary="Get all messages"
)
@error_handler
async def get_all_messages(query_params: ListRequestWithIsActive = Depends(make_dependable(ListRequestWithIsActive))):
	"""
	Get all messages. This API will return all the messages in the system.
	"""
	messages = MessageService().get_all_messages(query_params)

	return messages


@message_router.get(
	"/get_by_message_id/{message_id}", response_model=MessageResponse,
	status_code=status.HTTP_200_OK, tags=["Message APIs"],
	summary="Get message details by message id"
)
@error_handler
async def get_message_by_message_id(path_params: GetByMessageIdRequest = Depends()):
	"""
	Get message details by message id. This API will return the message details for the given message id.
	"""
	message = MessageService().get_message_by_message_id(path_params.message_id)

	return message


@message_router.get(
	"/get_by_id/{id}", response_model=MessageResponse,
	status_code=status.HTTP_200_OK, tags=["Message APIs"],
	summary="Get message details by message uuid"
)
@error_handler
async def get_message_by_id(path_params: GetByIdRequest = Depends()):
	"""
	Get message details by message uuid. This API will return the message details for the given message uuid.
	"""
	message = MessageService().get_message_by_id(path_params.id)

	return message


@message_router.get(
	"/search", response_model=Union[List[MessageResponse], int],
	status_code=status.HTTP_200_OK, tags=["Message APIs"],
	summary="Search messages"
)
@error_handler
async def search_message(query_params: SearchRequestWithIsActive = Depends(make_dependable(SearchRequestWithIsActive))):
	"""
	Search messages. This API will return the messages based on the search criteria.
	The API supports partial search as well.
	"""
	message = MessageService().search_message(query_params)

	return message


@message_router.put(
	"/trash",
	status_code=status.HTTP_200_OK, tags=["Message APIs"],
	summary="Delete the message and move to trash"
)
@error_handler
async def move_to_trash(request: BaseRequest):
	"""
	Move to trash folder. This API will deactivate the message or mark as inactive for the given message uuid (mandatory).
	"""
	message = MessageService().deactivate_message(request.id)

	return JSONResponse(
		content={
			"status": "success", "message": "Message moved to trash.",
			"message_id": message.message_id, "subject": message.subject
		},
		status_code=status.HTTP_200_OK
	)


@message_router.put(
	"/untrash",
	status_code=status.HTTP_200_OK, tags=["Message APIs"],
	summary="Untrashes the message and moves to inbox"
)
@error_handler
async def move_to_inbox(request: BaseRequest):
	"""
	Move to inbox folder. This API will activate the message or mark as active for the given message uuid (mandatory).
	"""
	message = MessageService().activate_message(request.id)

	return JSONResponse(
		content={
			"status": "success", "message": "Message moved to inbox.",
			"message_id": message.message_id, "subject": message.subject
		},
		status_code=status.HTTP_200_OK
	)
