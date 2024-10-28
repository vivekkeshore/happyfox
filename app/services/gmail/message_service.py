from uuid import UUID

from app.db_layer import BaseRepo, MessageLabelRepo
from app.lib import constants
from app.lib.custom_exceptions import RecordNotFoundError
from app.lib.singleton import Singleton
from app.models import Message, MessageLabelView, MessageAttachment, MessageLabel
from app.schema_models import ListRequestWithIsActive, SearchRequestWithIsActive
from app.services.common_service import CommonService
from app.services.gmail.message_label_service import MessageLabelService
from app.services.workflow.gmail_service import GmailService


class MessageService(metaclass=Singleton):
	@staticmethod
	def get_message_details(message_id: (str, UUID)) -> (MessageLabelView, MessageAttachment):
		try:
			message_label_view = CommonService.get_record_by_col(
				BaseRepo(MessageLabelView), "message_id", message_id
			)
		except RecordNotFoundError:
			message_label_view = None

		try:
			message_attachment = CommonService.get_record_by_col(
				BaseRepo(MessageAttachment), "message_id", message_id
			)
			message_attachment = [message_attachment] if isinstance(message_attachment, MessageAttachment) else message_attachment
		except RecordNotFoundError:
			message_attachment = None
		return message_label_view, message_attachment

	@staticmethod
	def get_message_by_id(message_id: (str, UUID)) -> Message:
		message = CommonService.get_record_by_id(BaseRepo(Message), message_id)
		message.labels, message.attachments = MessageService.get_message_details(message.message_id)
		return message

	@staticmethod
	def get_message_by_message_id(message_id: str) -> Message:
		message = CommonService.get_record_by_col(BaseRepo(Message), "message_id", message_id)
		message.labels, message.attachments = MessageService.get_message_details(message_id)
		return message

	@staticmethod
	def get_all_messages(query_params: ListRequestWithIsActive) -> [Message]:
		messages = CommonService.get_all_records(BaseRepo(Message), query_params)
		if query_params.count:
			return messages

		for message in messages:
			message.labels, message.attachments = MessageService.get_message_details(message.message_id)
		return messages

	@staticmethod
	def search_message(query_params: SearchRequestWithIsActive) -> [Message]:
		messages = CommonService.search_records(BaseRepo(Message), query_params)
		if query_params.count:
			return messages

		for message in messages:
			message.labels, message.attachments = MessageService.get_message_details(message.message_id)
		return messages

	@staticmethod
	def deactivate_message(message_id: (str, UUID)):
		message = CommonService.deactivate_record(BaseRepo(Message), message_id)
		message_id = message.message_id
		message_label = MessageLabelRepo().get_message_label_by_message_and_label_id(constants.LABEL_INBOX, message_id)
		if message_label:
			BaseRepo(MessageLabel).delete(message_label)

		MessageLabelService.create_message_label(message_id, constants.LABEL_TRASH)
		GmailService().move_labels(message_id, [constants.LABEL_INBOX], [constants.LABEL_TRASH])

		return message

	@staticmethod
	def activate_message(message_id: (str, UUID)):
		message = CommonService.activate_record(BaseRepo(Message), message_id)
		message_id = message.message_id
		message_label = MessageLabelRepo().get_message_label_by_message_and_label_id(constants.LABEL_TRASH, message_id)
		if message_label:
			BaseRepo(MessageLabel).delete(message_label)

		MessageLabelService.create_message_label(message_id, constants.LABEL_INBOX)
		GmailService().move_labels(message_id, [constants.LABEL_TRASH], [constants.LABEL_INBOX])

		return message

	@staticmethod
	def mark_as_read(message_id: (str, UUID)):
		message = CommonService.get_record_by_id(BaseRepo(Message), message_id)
		message.is_read = True
		return message
