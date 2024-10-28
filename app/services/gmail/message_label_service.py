from uuid import UUID

from fastapi.logger import logger

from app.db_layer import BaseRepo, MessageLabelRepo
from app.lib.custom_exceptions import DuplicateRecordError, CreateRecordException
from app.lib.singleton import Singleton
from app.models import MessageLabelView, MessageLabel
from app.schema_models import ListRequest, SearchRequest
from app.services.common_service import CommonService


class MessageLabelService(metaclass=Singleton):
	@staticmethod
	def get_message_label_by_id(message_label_id: (str, UUID)) -> MessageLabelView:
		message_label = CommonService.get_record_by_id(BaseRepo(MessageLabelView), message_label_id)
		return message_label

	@staticmethod
	def get_label_by_message_id(message_id: str) -> MessageLabelView:
		message_label = CommonService.get_record_by_col(BaseRepo(MessageLabelView), "message_id", message_id)
		return message_label

	@staticmethod
	def get_label_by_label_id(label_id: str) -> MessageLabelView:
		message_label = CommonService.get_record_by_col(BaseRepo(MessageLabelView), "label_id", label_id)
		return message_label

	@staticmethod
	def get_all_message_labels(query_params: ListRequest) -> [MessageLabelView]:
		message_labels = CommonService.get_all_records(BaseRepo(MessageLabelView), query_params)
		return message_labels

	@staticmethod
	def search_message_label(query_params: SearchRequest) -> [MessageLabelView]:
		message_label = CommonService.search_records(BaseRepo(MessageLabelView), query_params)
		return message_label

	@staticmethod
	def create_message_label(message_id: str, label_id: str):
		logger.info("Calling the Create message label service.")
		if not label_id:
			return

		message_label = MessageLabelRepo().get_message_label_by_message_and_label_id(label_id, message_id)

		if message_label:
			error_msg = f"Message label already exists with message id: {message_label.message_id} and label id: {label_id}"
			logger.error(error_msg)
			raise DuplicateRecordError(error_msg)

		try:
			message_label = BaseRepo(MessageLabel).create({"message_id": message_id, "label_id": label_id})
		except Exception as ex:
			error_msg = f"An Error has occurred while creating the new message label with message id: {message_id} and label id: {label_id}"
			logger.error(f"{error_msg}. Error - {ex}", exc_info=True)
			raise CreateRecordException(error_msg)

		logger.info(f"Message label created successfully with message id: {message_id} and label id: {label_id}")
