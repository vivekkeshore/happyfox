import json
import os
from datetime import datetime
from uuid import uuid4, UUID as UUID4

import dotenv
from sqlalchemy import Column, DateTime
from sqlalchemy import Index, String, Boolean, ForeignKey, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

dotenv.load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")
DB_HOST = os.environ.get("DB_HOST")
DB_DRIVER = os.environ.get("DB_DRIVER")

SQLALCHEMY_DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)
Base = declarative_base()


class BaseModel(Base):
	__abstract__ = True

	id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid4)

	def set_attributes(self, values):
		if not isinstance(values, dict):
			values = json.loads(values.json())

		for key, value in values.items():
			if (hasattr(self, key) and
					((isinstance(value, str) and value) or (isinstance(value, (bool, int, float, list, UUID4))))):
				setattr(self, key, value)


class AuditMixin(Base):
	__abstract__ = True

	created_at = Column(DateTime, nullable=False, default=datetime.now)
	updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


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


class MessageDetail(BaseModel, AuditMixin):
	__tablename__ = "message_detail"
	__table_args__ = (
		Index("idx_message_details_message_id", "message_id", unique=True),
		{"schema": "gmail"},
	)

	message_id = Column(String(32), ForeignKey(Message.message_id), nullable=False)
	text_body = Column(Text)
	html_body = Column(Text)


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
