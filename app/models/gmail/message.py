from sqlalchemy import Index, Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ARRAY

from app.models.base_model import BaseModel, AuditMixin


class Message(BaseModel, AuditMixin):
	__tablename__ = "message"
	__table_args__ = (
		Index("idx_message_message_id", "message_id", unique=True),
		Index("idx_message_thread_id", "thread_id"),
		Index("idx_message_subject", "subject"),
		Index("idx_message_from_address", "from_address"),
		{"schema": "gmail"},
	)
	message_id = Column(String(32), unique=True, nullable=False)
	thread_id = Column(String(32), nullable=False)
	from_address = Column(String(256), nullable=False)
	to = Column(ARRAY(String), nullable=False)
	cc = Column(ARRAY(String))
	bcc = Column(ARRAY(String))
	subject = Column(String(1024))
	received_at = Column(DateTime, nullable=False)
	is_active = Column(Boolean(), default=True, nullable=False)
