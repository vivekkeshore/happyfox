from dataclasses import field
from typing import Optional, List

from pydantic import BaseModel, Field, Extra, model_validator

from helpers.enum_models import RulePredicate, ActionType, Operation, FieldUnit, FieldType
from helpers.db_helpers.base_repo import BaseRepo
from helpers.db_models import Label
from helpers.field_rule import FIELD_RULE


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
	predicate: RulePredicate = Field(
		..., examples=["ANY", "ALL"]
	)
	rule_details: List[CreateRuleDetailRequest] = Field(..., min_length=1, title="Rule Details")
	actions: List[CreateRuleActionRequest] = Field(..., min_length=1, title="Actions")

	@model_validator(mode="before")
	def validate_labels(self):
		rule_details, actions = self.get("rule_details"), self.get("actions")

		for action in actions:
			if action.get("action") == ActionType.MOVE:
				if not action.get("value"):
					raise ValueError('Label value(s) is required for MOVE action.')

				else:
					labels = [label.strip() for label in action["value"].split(",")]
					for label in labels:
						repo = BaseRepo(Label)
						label_obj = repo.get_by_col("name", label)
						if not label_obj:
							raise ValueError(f'Label {label} is not a valid Gmail label.')
			else:
				if action.get("value"):
					raise ValueError(f'Value {action["value"]} is not allowed for {action.get("action")} action.')

		for rule_detail in rule_details:
			field_name = rule_detail.get("field_name")
			if field_name not in FIELD_RULE:
				raise ValueError(f"Field name {field_name} is not a valid field name.")

			if field_name != "received_at" and rule_detail.get("unit"):
				raise ValueError(f"Unit is not allowed for filter field {field_name}.")

			allowed_operations = FIELD_RULE[field_name].get("allowed_operations")
			if rule_detail.get("operation") not in allowed_operations:
				raise ValueError(f"Operation {rule_detail.get('operation')} is not allowed for field {field_name}.")

			if FIELD_RULE[field_name].get("field_type") == FieldType.NUMBER and not rule_detail.get("value").isdigit():
				raise ValueError(f"Value {rule_detail.get('value')} is not a valid number for field {field_name}")
			elif FIELD_RULE[field_name].get("field_type") == FieldType.BOOLEAN and rule_detail.get("value").lower() not in ["true", "false"]:
				raise ValueError(f"Value {rule_detail.get('value')} is not a valid boolean (true/false) for field {field_name}")

		return self
