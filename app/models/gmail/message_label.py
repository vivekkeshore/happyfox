from sqlalchemy import Index, Column, String, ForeignKey

from app.models.base_model import BaseModel, AuditMixin, Base
from app.models.gmail.label import Label
from app.models.gmail.message import Message


class MessageLabel(BaseModel, AuditMixin):
	__tablename__ = "message_label"
	__table_args__ = (
		Index("idx_message_label_message_id", "message_id", unique=False),
		Index("idx_message_label_label_id", "label_id", unique=False),
		{"schema": "gmail"},
	)
	message_id = Column(String(32), ForeignKey(Message.message_id), nullable=False)
	label_id = Column(String(32), ForeignKey(Label.label_id), nullable=False)


class MessageLabelView(Base):
	__tablename__ = "message_label_view"
	__table_args__ = (
		{"schema": "gmail"},
	)
	message_id = Column(String(32), primary_key=True)
	label_id = Column(String(32), primary_key=True)
	name = Column(String(256), primary_key=True)
	label_type = Column(String(256), primary_key=True)
