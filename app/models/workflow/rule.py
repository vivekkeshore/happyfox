from sqlalchemy import Index, Column, String, Enum

from app.models.base_model import BaseModel, AuditMixin
from app.models.enum_model import RulePredicate


class Rule(BaseModel, AuditMixin):
	__tablename__ = "rule"
	__table_args__ = (
		Index("idx_filter_rule_name", "name", unique=True),
		{"schema": "workflow"},
	)
	name = Column(String(256), nullable=False, unique=True)
	description = Column(String(512))
	predicate = Column(Enum(RulePredicate, name="rule_predicate", schema="workflow"), nullable=False)
