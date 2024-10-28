from sqlalchemy import Index, Column, String, Boolean

from app.models.base_model import BaseModel, AuditMixin


class Label(BaseModel, AuditMixin):
	__tablename__ = "label"
	__table_args__ = (
		Index("idx_label_label_id", "label_id", unique=True),
		Index("idx_label_name", "name", unique=True),
		{"schema": "gmail"},
	)
	label_id = Column(String(32), nullable=False, unique=True)
	name = Column(String(256), nullable=False, unique=True)
	type_ = Column("type", String(50), nullable=False)
	is_active = Column(Boolean(), default=True, nullable=False)
