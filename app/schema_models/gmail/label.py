from fastapi import Path
from pydantic import BaseModel, Field, UUID4, Extra


class GetByLabelIdRequest(BaseModel, extra=Extra.forbid):
	label_id: str = Path(
		..., title="Label id", examples=["INBOX"],
		min_length=1, max_length=32
	)


class LabelResponse(BaseModel):
	id: UUID4 = Field(..., title="Label id UUID")
	label_id: str = Field(..., title="Label id")
	name: str = Field(..., title="Label name")
	type_: str = Field(..., title="Label type", serialization_alias="type")
	is_active: bool = Field(..., title="Label is active")
