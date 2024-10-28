from sqlalchemy import Index, Column, String, Text, ForeignKey

from app.models.base_model import BaseModel, AuditMixin
from app.models.gmail.message import Message


class MessageDetail(BaseModel, AuditMixin):
	__tablename__ = "message_detail"
	__table_args__ = (
		Index("idx_message_details_message_id", "message_id", unique=True),
		{"schema": "gmail"},
	)

	message_id = Column(String(32), ForeignKey(Message.message_id), nullable=False)
	text_body = Column(Text)
	html_body = Column(Text)
