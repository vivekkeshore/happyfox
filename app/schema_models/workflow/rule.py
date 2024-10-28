from datetime import datetime
from typing import Optional, List, Union
from uuid import UUID

from pydantic import BaseModel, Field, Extra

from app.lib.constants import UUID_REGEX
from app.models.enum_model import RulePredicate, ActionType, Operation, FieldUnit


class ExecuteByNameRequest(BaseModel, extra=Extra.forbid):
	name: str = Field(
		..., max_length=256, min_length=1, examples=["foobar"]
	)
	execute_actions: bool = Field(
		False, title="Execute Actions", examples=[True, False]
	)


class ExecuteByIdRequest(BaseModel, extra=Extra.forbid):
	id: str = Field(..., pattern=UUID_REGEX, description="ID of the rule or rule id uuid.")
	execute_actions: bool = Field(
		False, title="Execute Actions", examples=[True, False]
	)


class CreateRuleDetailRequest(BaseModel, extra=Extra.forbid):
	field_name: str = Field(..., min_length=1, max_length=256, title="Field Name")
	operation: Operation = Field(..., title="Operation")
	value: str = Field(..., min_length=1, max_length=256, title="Value")
	unit: Optional[FieldUnit] = Field(None, title="Unit")


class CreateRuleActionRequest(BaseModel, extra=Extra.forbid):
	action: ActionType = Field(..., title="Action")
	value: Optional[str] = Field(None, min_length=1, max_length=256, title="Value")


class CreateRuleRequest(BaseModel, extra=Extra.forbid):
	name: str = Field(
		..., min_length=4, max_length=256,
		examples=["Rule 1", "Rule 2", "Rule 3"]
	)
	description: Optional[str] = Field(
		None, min_length=10, max_length=512,
		examples=["This is a rule", "This is another rule"]
	)
	predicate: RulePredicate = Field(
		..., examples=["ANY", "ALL"]
	)
	rule_details: List[CreateRuleDetailRequest] = Field(..., min_length=1, title="Rule Details")
	actions: List[CreateRuleActionRequest] = Field(..., min_length=1, title="Actions")


class RuleDetailResponse(BaseModel, extra=Extra.forbid):
	id: UUID = Field(..., title="ID")
	rule_id: UUID = Field(..., title="Rule ID")
	field_name: str = Field(..., title="Field Name")
	filter_field_id: UUID = Field(..., title="Filter Field ID")
	operation: Operation = Field(..., title="Operation")
	value: str = Field(..., title="Value")
	unit: Optional[FieldUnit] = Field(None, title="Unit")
	created_at: datetime = Field(..., title="Created At")
	updated_at: datetime = Field(..., title="Updated At")


class RuleActionResponse(BaseModel, extra=Extra.forbid):
	id: UUID = Field(..., title="ID")
	rule_id: UUID = Field(..., title="Rule ID")
	action: ActionType = Field(..., title="Action")
	value: Union[Optional[str], Optional[List[str]]] = Field(None, title="Value")
	created_at: datetime = Field(..., title="Created At")
	updated_at: datetime = Field(..., title="Updated At")


class RuleResponse(BaseModel, extra=Extra.forbid):
	id: UUID = Field(..., title="ID")
	name: str = Field(..., title="Name")
	description: Optional[str] = Field(None, title="Description")
	predicate: RulePredicate = Field(..., title="Predicate")
	rule_details: List[RuleDetailResponse] = Field(..., title="Rule Details")
	actions: List[RuleActionResponse] = Field(..., title="Actions")
	created_at: datetime = Field(..., title="Created At")
	updated_at: datetime = Field(..., title="Updated At")
