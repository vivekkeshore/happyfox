from sqlalchemy import Index, Column, ForeignKey, String, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import BaseModel, AuditMixin
from app.models.enum_model import Operation, FieldUnit
from app.models.workflow.filter_field import FilterField
from app.models.workflow.rule import Rule


class RuleDetail(BaseModel, AuditMixin):
	__tablename__ = "rule_detail"
	__table_args__ = (
		Index("idx_rule_detail_rule_id", "rule_id", unique=False),
		Index("idx_rule_detail_filter_field_id", "filter_field_id", unique=False),
		{"schema": "workflow"},
	)
	rule_id = Column(UUID(as_uuid=True), ForeignKey(Rule.id), nullable=False)
	field_name = Column(String(256), nullable=False)
	filter_field_id = Column(UUID(as_uuid=True), ForeignKey(FilterField.id), nullable=False)
	operation = Column(Enum(Operation, name="operation", schema="workflow"), nullable=False)
	value = Column(String(256), nullable=False)
	unit = Column(Enum(FieldUnit, name="field_unit", schema="workflow"), nullable=True)
