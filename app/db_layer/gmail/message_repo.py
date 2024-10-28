from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import func, any_, exists, and_, or_
from sqlalchemy.dialects.postgresql import ARRAY

from app.db_layer.base_repo import BaseRepo
from app.db_layer.sql_context import SqlContext
from app.lib.singleton import Singleton
from app.models.enum_model import Operation, FieldUnit, RulePredicate
from app.models.gmail import Message, MessageDetail, MessageAttachment, MessageLabelView
from app.models.workflow import Rule

MODEL_MAP = {
	"Message": Message,
	"MessageDetail": MessageDetail,
	"MessageAttachment": MessageAttachment,
	"MessageLabel": MessageLabelView
}

OPERATOR_MAP = {
	Operation.EQUALS: "__eq__",
	Operation.NOT_EQUALS: "__ne__",
	Operation.GREATER_THAN: "__gt__",
	Operation.GREATER_THAN_EQUALS: "__ge__",
	Operation.LESS_THAN: "__lt__",
	Operation.LESS_THAN_EQUALS: "__le__",
	Operation.IN: "in_",
	Operation.NOT_IN: "not_in",
	Operation.CONTAINS: "ilike",
	Operation.NOT_CONTAINS: "not_ilike",
}

BOOLEAN_OPERATION_MAP = {
	Operation.EQUALS: "is_",
	Operation.NOT_EQUALS: "not_is",
}

DATETIME_DELTA_ARG = {
	FieldUnit.MINUTES: "minutes",
	FieldUnit.HOURS: "hours",
	FieldUnit.DAYS: "days",
	FieldUnit.MONTHS: "months",
	FieldUnit.YEARS: "years",
}


class MessageRepo(BaseRepo, metaclass=Singleton):
	def __init__(self):
		super().__init__(Message)

	@staticmethod
	def _get_query_expression_for_column(column, operation, value):
		operation_method = OPERATOR_MAP.get(operation)
		if isinstance(column.type, bool):
			operation_method = BOOLEAN_OPERATION_MAP.get(operation)
			value = True if value.lower() == "true" else False

		if operation in [Operation.IN, Operation.NOT_IN]:
			value = [item.strip() for item in value.split(",")]

		if isinstance(column.type, ARRAY):
			if operation in [Operation.CONTAINS, Operation.NOT_CONTAINS]:
				expr = getattr(func.array_to_string(column, ' '), operation_method)(f"%{value}%")
			else:
				expr = getattr(column, operation_method)(any_(value))

		else:
			if operation in [Operation.CONTAINS, Operation.NOT_CONTAINS]:
				expr = getattr(column, operation_method)(f"%{value}%")
			else:
				expr = getattr(column, operation_method)(value)

		return expr

	def execute_rule(self, rule: Rule):
		query = self.query.distinct()
		expressions = []
		joined_tables = set()
		for rule_detail in rule.rule_details:
			model = MODEL_MAP.get(rule_detail.filter_field.table)
			if rule_detail.filter_field.is_column:
				column = getattr(model, rule_detail.filter_field.column)
				if rule_detail.filter_field.column == "received_at":
					rule_detail.value = datetime.now() - relativedelta(
						**{DATETIME_DELTA_ARG.get(rule_detail.unit): int(rule_detail.value)}
					)

				if model == self.model:
					expr = self._get_query_expression_for_column(column, rule_detail.operation, rule_detail.value)
				else:
					if model not in joined_tables:
						query = query.join(model, getattr(model, "message_id") == self.model.message_id, isouter=True)
						joined_tables.add(model)

					expr = self._get_query_expression_for_column(column, rule_detail.operation, rule_detail.value)
				expressions.append(expr)

			else:
				if isinstance(rule_detail.filter_field.field_type, bool):
					is_having_records = True if rule_detail.value.lower() == "true" else False
					if is_having_records:
						expr = exists().where(getattr(model, "message_id") == self.model.message_id)
					else:
						expr = ~exists().where(getattr(model, "message_id") == self.model.message_id)

					expressions.append(expr)

		predicate = and_ if rule.predicate == RulePredicate.ALL else or_
		query = query.where(predicate(*expressions))

		with SqlContext() as sql_context:
			result = sql_context.execute(query)

		return result.scalars().all()
