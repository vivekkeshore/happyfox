from pydantic import BaseModel, Field


class MessageLabelResponse(BaseModel):
	message_id: str = Field(..., title="Message id")
	label_id: str = Field(..., title="Label id")
	name: str = Field(..., title="Label name")
	label_type: str = Field(..., title="Label type")

