from uuid import UUID

from app.db_layer import BaseRepo
from app.lib.singleton import Singleton
from app.models import Label
from app.schema_models import ListRequestWithIsActive, SearchRequestWithIsActive
from app.services.common_service import CommonService


class LabelService(metaclass=Singleton):
	@staticmethod
	def get_label_by_id(label_id: (str, UUID)) -> Label:
		label = CommonService.get_record_by_id(BaseRepo(Label), label_id)
		return label

	@staticmethod
	def get_label_by_label_id(label_id: str) -> Label:
		label = CommonService.get_record_by_col(BaseRepo(Label), "label_id", label_id)
		return label

	@staticmethod
	def get_label_by_name(name: str) -> Label:
		label = CommonService.get_record_by_col(BaseRepo(Label), "name", name)
		return label

	@staticmethod
	def get_all_labels(query_params: ListRequestWithIsActive) -> [Label]:
		labels = CommonService.get_all_records(BaseRepo(Label), query_params)
		return labels

	@staticmethod
	def search_label(query_params: SearchRequestWithIsActive) -> [Label]:
		label = CommonService.search_records(BaseRepo(Label), query_params)
		return label

	@staticmethod
	def deactivate_label(label_id: (str, UUID)):
		label = CommonService.deactivate_record(BaseRepo(Label), label_id)
		return label

	@staticmethod
	def activate_label(label_id: (str, UUID)):
		label = CommonService.activate_record(BaseRepo(Label), label_id)
		return label
