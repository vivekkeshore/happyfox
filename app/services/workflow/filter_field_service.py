from uuid import UUID

from app.db_layer import BaseRepo
from app.lib.singleton import Singleton
from app.models import FilterField
from app.schema_models import ListRequest, SearchRequest
from app.services.common_service import CommonService


class FilterFieldService(metaclass=Singleton):
	@staticmethod
	def get_filter_field_by_id(filter_field_id: (str, UUID)) -> FilterField:
		filter_field = CommonService.get_record_by_id(BaseRepo(FilterField), filter_field_id)
		return filter_field

	@staticmethod
	def get_filter_field_by_name(filter_field_name: str) -> FilterField:
		filter_field = CommonService.get_record_by_col(BaseRepo(FilterField), "field_name", filter_field_name)
		return filter_field

	@staticmethod
	def get_all_filter_fields(query_params: ListRequest) -> [FilterField]:
		filter_fields = CommonService.get_all_records(BaseRepo(FilterField), query_params)
		return filter_fields

	@staticmethod
	def search_filter_field(query_params: SearchRequest) -> [FilterField]:
		filter_field = CommonService.search_records(BaseRepo(FilterField), query_params)
		return filter_field
