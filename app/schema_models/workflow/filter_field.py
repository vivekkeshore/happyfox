from typing import Optional

from pydantic import BaseModel, Field, UUID4

from app.models.enum_model import FieldType, Operation


class FilterFieldResponse(BaseModel):
	id: UUID4 = Field(..., description="ID of the Filter Field.")
	field_name: str = Field(..., description="Name of the Filter Field.")
	field_type: FieldType = Field(..., description="Type of the Filter Field.")
	allowed_operations: list[Operation] = Field(..., description="Allowed operations on the Filter Field.")
	is_column: bool = Field(..., description="Is the Filter Field a column.")
	schema: Optional[str] = Field(None, description="Schema of the Filter Field.")
	table: Optional[str] = Field(None, description="Table of the Filter Field.")
	column: Optional[str] = Field(None, description="Column of the Filter Field.")