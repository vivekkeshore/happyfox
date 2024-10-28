from sqlalchemy import Index, Column, String, ForeignKey, Integer

from app.models.base_model import BaseModel, AuditMixin
from app.models.gmail.message import Message


class MessageAttachment(BaseModel, AuditMixin):
	__tablename__ = "message_attachment"
	__table_args__ = (
		Index("idx_message_attachment_message_id", "message_id", unique=False),
		{"schema": "gmail"},
	)
	message_id = Column(String(32), ForeignKey(Message.message_id), nullable=False)
	file_name = Column(String(512), nullable=False)
	file_url = Column(String(4096), nullable=True)
	mime_type = Column(String(256), nullable=False)
	size = Column(Integer(), nullable=False)
	attachment_id = Column(String(1024), nullable=False)
