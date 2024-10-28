from sqlalchemy import Index, Column, String, Enum, Boolean
from sqlalchemy.dialects.postgresql import ARRAY

from app.models.base_model import BaseModel, AuditMixin
from app.models.enum_model import FieldType, Operation


class FilterField(BaseModel, AuditMixin):
	__tablename__ = "filter_field"
	__table_args__ = (
		Index("idx_filter_field_field_name", "field_name", unique=True),
		{"schema": "workflow"},
	)
	field_name = Column(String(256), nullable=False, unique=True)
	field_type = Column(Enum(FieldType, name="filter_field_type", schema="workflow"), nullable=False)
	allowed_operations = Column(ARRAY(Enum(Operation, name="operation", schema="workflow")), nullable=False)
	is_column = Column(Boolean(), nullable=False)
	schema = Column(String(256))
	table = Column(String(256))
	column = Column(String(256))
