from uuid import UUID

from app.db_layer import BaseRepo
from app.lib.singleton import Singleton
from app.models import MessageDetail
from app.schema_models import ListRequest, SearchRequest
from app.services.common_service import CommonService


class MessageDetailService(metaclass=Singleton):
	@staticmethod
	def get_message_detail_by_id(message_detail_id: (str, UUID)) -> MessageDetail:
		message_detail = CommonService.get_record_by_id(BaseRepo(MessageDetail), message_detail_id)
		return message_detail

	@staticmethod
	def get_all_message_details(query_params: ListRequest) -> [MessageDetail]:
		message_details = CommonService.get_all_records(BaseRepo(MessageDetail), query_params)
		return message_details

	@staticmethod
	def search_message_detail(query_params: SearchRequest) -> [MessageDetail]:
		message_detail = CommonService.search_records(BaseRepo(MessageDetail), query_params)
		return message_detail
