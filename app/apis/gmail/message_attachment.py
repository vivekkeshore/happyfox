from typing import List, Union

from fastapi import APIRouter, status, Depends

from app.lib.exception_handler import error_handler
from app.lib.pydantic_helper import make_dependable
from app.schema_models import ListRequest, GetByMessageIdRequest, GetByIdRequest
from app.schema_models import SearchRequest, MessageAttachmentResponse
from app.services import MessageAttachmentService

message_attachment_router = APIRouter()


@message_attachment_router.get(
	"/list", response_model=Union[List[MessageAttachmentResponse], int],
	status_code=status.HTTP_200_OK, tags=["Message Attachment APIs"],
	summary="Get all message attachments"
)
@error_handler
async def get_all_message_attachments(query_params: ListRequest = Depends(make_dependable(ListRequest))):
	"""
	Get all message attachments. This API will return all the message attachments in the system.
	"""
	attachments = MessageAttachmentService().get_all_message_attachments(query_params)

	return attachments


@message_attachment_router.get(
	"/get_by_id/{id}", response_model=MessageAttachmentResponse,
	status_code=status.HTTP_200_OK, tags=["Message Attachment APIs"],
	summary="Get message attachment by message attachment uuid"
)
@error_handler
async def get_message_attachment_by_attachment_id(path_params: GetByIdRequest = Depends()):
	"""
	Get message attachment by message attachment uuid. This API will return the message attachment for the given message attachment uuid.
	"""
	attachment = MessageAttachmentService().get_message_attachment_by_id(path_params.id)

	return attachment


@message_attachment_router.get(
	"/get_by_message_id/{message_id}", response_model=Union[List[MessageAttachmentResponse], MessageAttachmentResponse],
	status_code=status.HTTP_200_OK, tags=["Message Attachment APIs"],
	summary="Get attachments by message id"
)
@error_handler
async def get_message_attachment_by_message_id(path_params: GetByMessageIdRequest = Depends()):
	"""
	Get message attachments by message id. This API will return the message attachment for the given message id.
	"""
	attachment = MessageAttachmentService().get_message_attachment_by_message_id(path_params.message_id)

	return attachment


@message_attachment_router.get(
	"/search", response_model=Union[List[MessageAttachmentResponse], int],
	status_code=status.HTTP_200_OK, tags=["Message Attachment APIs"],
	summary="Search attachments"
)
@error_handler
async def search_attachment(query_params: SearchRequest = Depends(make_dependable(SearchRequest))):
	"""
	Search message attachments. This API will return the message attachments based on the search criteria.
	The API supports partial search as well.
	"""
	attachment = MessageAttachmentService().search_message_attachment(query_params)

	return attachment
