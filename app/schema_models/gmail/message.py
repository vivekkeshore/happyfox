import datetime
from typing import Optional, List

from fastapi import Path
from pydantic import BaseModel, Field, UUID4, Extra


class GetByMessageIdRequest(BaseModel, extra=Extra.forbid):
	message_id: str = Path(
		..., title="Message id", examples=["192433992f1c24da"],
		min_length=16, max_length=32
	)


class Attachments(BaseModel):
	message_id: str = Field(..., title="Message id")
	file_name: str = Field(..., title="File name")
	mime_type: str = Field(..., title="Mime type of file")
	size: int = Field(..., title="Size of file")
	file_url: Optional[str] = Field(None, title="File path in s3 or other storage")
	attachment_id: str = Field(..., title="Attachment id")


class Labels(BaseModel):
	label_id: str = Field(..., title="Label id")
	name: str = Field(..., title="Label name")
	label_type: str = Field(..., title="Label type like system or user")


class MessageResponse(BaseModel):
	id: UUID4 = Field(..., title="Message id")
	message_id: str = Field(..., title="Message id")
	thread_id: str = Field(..., title="Thread id")
	from_address: str = Field(..., title="From address")
	to: list[str] = Field(..., title="To address")
	cc: Optional[list[str]] = Field(None, title="CC address")
	bcc: Optional[list[str]] = Field(None, title="BCC address")
	subject: Optional[str] = Field(None, title="Subject")
	received_at: datetime.datetime = Field(..., title="Received at")
	is_active: bool = Field(..., title="Is active")
	attachments: Optional[List[Attachments]] = Field(None, title="Attachments")
	labels: Optional[List[Labels]] = Field(None, title="Labels")


class MessageMinimalResponse(BaseModel):
	message_id: str = Field(..., title="Message id")
	from_address: str = Field(..., title="From address")
	subject: Optional[str] = Field(None, title="Subject")
