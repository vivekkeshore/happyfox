from typing import Optional

from pydantic import BaseModel, Field, UUID4


class MessageBodyResponse(BaseModel):
	id: UUID4 = Field(..., title="Message id uuid")
	message_id: str = Field(..., title="Message id")
	text_body: Optional[str] = Field(None, title="Text Body")
	html_body: Optional[str] = Field(None, title="HTML Body")
