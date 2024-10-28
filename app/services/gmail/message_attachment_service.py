from uuid import UUID

from app.db_layer import BaseRepo
from app.lib.singleton import Singleton
from app.models import MessageAttachment
from app.schema_models import ListRequest, SearchRequest
from app.services.common_service import CommonService


class MessageAttachmentService(metaclass=Singleton):
	@staticmethod
	def get_message_attachment_by_id(message_attachment_id: (str, UUID)) -> MessageAttachment:
		message_attachment = CommonService.get_record_by_id(BaseRepo(MessageAttachment), message_attachment_id)
		return message_attachment

	@staticmethod
	def get_message_attachment_by_message_id(message_id: str) -> [MessageAttachment]:
		message_attachments = CommonService.get_record_by_col(BaseRepo(MessageAttachment), 'message_id', message_id)
		return message_attachments

	@staticmethod
	def get_all_message_attachments(query_params: ListRequest) -> [MessageAttachment]:
		message_attachments = CommonService.get_all_records(BaseRepo(MessageAttachment), query_params)
		return message_attachments

	@staticmethod
	def search_message_attachment(query_params: SearchRequest) -> [MessageAttachment]:
		message_attachment = CommonService.search_records(BaseRepo(MessageAttachment), query_params)
		return message_attachment
