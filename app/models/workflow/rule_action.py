from sqlalchemy import Index, Column, ForeignKey, String, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import BaseModel, AuditMixin
from app.models.enum_model import ActionType
from app.models.workflow.rule import Rule


class RuleAction(BaseModel, AuditMixin):
	__tablename__ = "rule_action"
	__table_args__ = (
		Index("idx_rule_action_rule_id", "rule_id", unique=False),
		{"schema": "workflow"},
	)
	rule_id = Column(UUID(as_uuid=True), ForeignKey(Rule.id), nullable=False)
	action = Column(Enum(ActionType, name="action_type", schema="workflow"), nullable=False)
	value = Column(String(256), nullable=True)
