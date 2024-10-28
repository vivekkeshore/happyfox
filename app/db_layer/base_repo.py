import re
from uuid import UUID

from pydantic import BaseModel as BaseModelSchema
from sqlalchemy import select, String, func, any_
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql.sqltypes import Enum

from app.db_layer.sql_context import SqlContext
from app.models.base_model import BaseModel

UUID_REGEX = "[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}"

class BaseRepo:
	def __init__(self, model):
		self.model = model
		self.query = select(model)

	def get_by_id(self, record_id):
		query = self.query.where(
			self.model.id == str(record_id)
		)

		with SqlContext() as sql_context:
			result = sql_context.execute(query)

		return result.scalar()

	def get_by_col(self, col: str, value: (str, UUID, int, float)):
		query = self.query.where(
			getattr(self.model, col) == value
		)

		with SqlContext() as sql_context:
			result = sql_context.execute(query)

		return result.scalars().all()

	def search_by_col(self, col, value):
		result = self.query.where(
			getattr(self.model, col).ilike(f"%{value}%")
		)

		with SqlContext() as sql_context:
			result = sql_context.execute(result)

		return result.scalars().all()

	def get_all_query(self, query_params: BaseModelSchema, ilike: bool = False) -> [BaseModel]:
		query = self.query
		if ilike and (re.match(UUID_REGEX, query_params.value)):
			ilike = False

		if hasattr(query_params, "col") and query_params.col is not None:
			model_col = getattr(self.model, query_params.col)
			model_col_type = model_col.expression.type
			if isinstance(model_col_type, ARRAY):
				model_col_type = model_col.expression.type.item_type

			if not isinstance(model_col_type, String) or isinstance(model_col_type, Enum):
				ilike = False

			if isinstance(model_col.type, ARRAY):
				query = query.where(
					query_params.value == any_(model_col)
					if not ilike else
					func.array_to_string(model_col, ' ').ilike(f"%{query_params.value}%")
				)

			else:
				query = query.where(
					model_col == str(query_params.value)
					if not ilike else
					model_col.ilike(f"%{query_params.value}%")
				)

		if (
			hasattr(query_params, 'is_active') and hasattr(self.model, 'is_active')
			and query_params.is_active is not None
		):
			query = query.where(self.model.is_active.is_(query_params.is_active))

		return query

	def get_all(self, query_params: BaseModelSchema, ilike: bool = False) -> [BaseModel]:
		query = self.get_all_query(query_params, ilike)
		if query_params.page and query_params.per_page:
			query = query.offset(
				(query_params.page - 1) * query_params.per_page
			).limit(query_params.per_page)

		with SqlContext() as sql_context:
			result = sql_context.execute(query)
			result = result.scalars().all()

		return len(result) if query_params.count else result

	@staticmethod
	def update(record: BaseModel, record_data: (BaseModelSchema, dict), commit: bool = True):
		record.set_attributes(record_data)

		if commit:
			with SqlContext() as sql_context:
				sql_context.session.add(record)

		return record

	def create(self, record_data: (BaseModelSchema, dict), commit: bool = True):
		record = self.model()
		record = self.update(record, record_data, commit)

		return record

	@staticmethod
	def delete(record: BaseModel):
		with SqlContext() as sql_context:
			sql_context.session.delete(record)

	@staticmethod
	def activate_deactivate_record(record: BaseModel, is_active: bool = True):
		record.is_active = is_active

		with SqlContext() as sql_context:
			sql_context.session.add(record)

		return record
