from enum import Enum

class BaseEnum(str, Enum):
	@classmethod
	def values(cls):
		return [member for member in cls.__members__]

class Operation(BaseEnum):
	EQUALS = "EQUALS"
	NOT_EQUALS = "NOT_EQUALS"
	CONTAINS = "CONTAINS"
	NOT_CONTAINS = "NOT_CONTAINS"
	LESS_THAN = "LESS_THAN"
	GREATER_THAN = "GREATER_THAN"
	LESS_THAN_EQUALS = "LESS_THAN_EQUALS"
	GREATER_THAN_EQUALS = "GREATER_THAN_EQUALS"
	IN = "IN"
	NOT_IN = "NOT_IN"


class FieldType(BaseEnum):
	STRING = "STRING"
	NUMBER = "NUMBER"
	BOOLEAN = "BOOLEAN"
	DATETIME = "DATETIME"


class FieldUnit(BaseEnum):
	MINUTES = "MINUTES"
	HOURS = "HOURS"
	DAYS = "DAYS"
	MONTHS = "MONTHS"
	YEARS = "YEARS"


class RulePredicate(BaseEnum):
	ANY = "ANY"
	ALL = "ALL"


class ActionType(BaseEnum):
	MOVE = "MOVE"
	MARK_AS_READ = "MARK_AS_READ"
	MARK_AS_UNREAD = "MARK_AS_UNREAD"
	DELETE = "DELETE"
