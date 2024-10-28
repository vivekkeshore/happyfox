from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageAttachmentResponse(BaseModel):
	id: UUID = Field(..., title="Attachment id uuid")
	message_id: str = Field(..., title="Message id")
	file_name: str = Field(..., title="File name")
	file_url: Optional[str] = Field(None, title="File url")
	mime_type: str = Field(..., title="Mime type")
	size: int = Field(..., title="Size")
	attachment_id: str = Field(..., title="Attachment id")

