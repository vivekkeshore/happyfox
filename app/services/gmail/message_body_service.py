from app.db_layer import BaseRepo
from app.lib.singleton import Singleton
from app.models import MessageDetail
from app.schema_models import SearchRequest
from app.services.common_service import CommonService


class MessageBodyService(metaclass=Singleton):
	@staticmethod
	def get_message_body_by_message_id(message_id: str) -> MessageDetail:
		message_label = CommonService.get_record_by_col(BaseRepo(MessageDetail), "message_id", message_id)
		return message_label

	@staticmethod
	def search_message_body(query_params: SearchRequest) -> [MessageDetail]:
		message_label = CommonService.search_records(BaseRepo(MessageDetail), query_params)
		return message_label
