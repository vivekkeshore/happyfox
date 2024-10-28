from uuid import UUID, uuid4

from fastapi.logger import logger

from app.db_layer import BaseRepo, MessageRepo, MessageLabelRepo
from app.db_layer.sql_context import SqlContext
from app.lib.constants import LABEL_UNREAD, LABEL_READ
from app.lib.custom_exceptions import DuplicateRecordError, InvalidDataException
from app.lib.custom_exceptions import RecordNotFoundError
from app.lib.singleton import Singleton
from app.models import Rule, RuleAction, RuleDetail, Message, MessageLabel
from app.models.enum_model import FieldType, ActionType
from app.schema_models import ListRequest, SearchRequest, CreateRuleRequest
from app.services import MessageLabelService, GmailService, MessageService
from app.services.common_service import CommonService
from app.services.gmail.label_service import LabelService
from app.services.workflow.filter_field_service import FilterFieldService


class RuleService(metaclass=Singleton):
	@staticmethod
	def get_rule_details_by_rule_id(rule_id: (str, UUID), get_filter_field_detail: bool = False) -> [RuleDetail]:
		rule_details = CommonService.get_record_by_col(BaseRepo(RuleDetail), "rule_id", rule_id)

		if get_filter_field_detail:
			for rule_detail in rule_details:
				rule_detail.filter_field = FilterFieldService().get_filter_field_by_id(rule_detail.filter_field_id)

		return rule_details if isinstance(rule_details, list) else [rule_details]

	@staticmethod
	def get_rule_actions_by_rule_id(rule_id: (str, UUID)) -> [RuleAction]:
		rule_actions = CommonService.get_record_by_col(BaseRepo(RuleAction), "rule_id", rule_id)
		return rule_actions if isinstance(rule_actions, list) else [rule_actions]

	@staticmethod
	def get_rule_by_id(rule_id: (str, UUID), get_filter_field_detail: bool = False) -> Rule:
		rule = CommonService.get_record_by_id(BaseRepo(Rule), rule_id)
		rule.rule_details = RuleService.get_rule_details_by_rule_id(rule_id, get_filter_field_detail)
		rule.actions = RuleService.get_rule_actions_by_rule_id(rule_id)
		return rule

	@staticmethod
	def get_rule_by_name(rule_name: str, get_filter_field_detail: bool = False) -> Rule:
		rule = CommonService.get_record_by_name(BaseRepo(Rule), rule_name)
		rule.rule_details = RuleService.get_rule_details_by_rule_id(rule.id, get_filter_field_detail)
		rule.actions = RuleService.get_rule_actions_by_rule_id(rule.id)
		return rule

	@staticmethod
	def get_all_rules(query_params: ListRequest) -> [Rule]:
		rules = CommonService.get_all_records(BaseRepo(Rule), query_params)
		if not query_params.count:
			for rule in rules:
				rule.rule_details = RuleService.get_rule_details_by_rule_id(rule.id)
				rule.actions = RuleService.get_rule_actions_by_rule_id(rule.id)

		return rules

	@staticmethod
	def search_rule(query_params: SearchRequest) -> [Rule]:
		rules = CommonService.search_records(BaseRepo(Rule), query_params)
		if not query_params.count:
			for rule in rules:
				rule.rule_details = RuleService.get_rule_details_by_rule_id(rule.id)
				rule.actions = RuleService.get_rule_actions_by_rule_id(rule.id)
		return rules

	@staticmethod
	def _validate_rule_details(request_body: CreateRuleRequest) -> (CreateRuleRequest, dict):
		logger.info("Validating the rule details.")
		filter_field_map = {}
		for rule_detail in request_body.rule_details:
			if rule_detail.field_name != "received_at" and rule_detail.unit:
				error_msg = f"Unit is not allowed for filter field {rule_detail.field_name}"
				logger.error(error_msg)
				raise InvalidDataException(error_msg)

			filter_field = FilterFieldService().get_filter_field_by_name(rule_detail.field_name)
			logger.info(
				f"Validating rule detail. Field name - {filter_field.field_name} | Operation - {rule_detail.operation}"
			)

			if rule_detail.operation not in filter_field.allowed_operations:
				error_msg = f"Operation {rule_detail.operation} is not allowed for filter field {filter_field.field_name}"
				logger.error(error_msg)
				raise InvalidDataException(error_msg)

			if filter_field.field_type == FieldType.NUMBER:
				if not rule_detail.value.isdigit():
					error_msg = f"Value {rule_detail.value} is not a valid number for filter field {filter_field.field_name}"
					logger.error(error_msg)
					raise InvalidDataException(error_msg)

			elif filter_field.field_type == FieldType.BOOLEAN:
				if rule_detail.value.lower() not in ["true", "false"]:
					error_msg = f"Value {rule_detail.value} is not a valid boolean for filter field {filter_field.field_name}"
					logger.error(error_msg)
					raise InvalidDataException(error_msg)

			filter_field_map[filter_field.field_name] = str(filter_field.id)

		logger.info("Rule details validated successfully.")
		return request_body, filter_field_map

	@staticmethod
	def _validate_rule_actions(request_body: CreateRuleRequest) -> CreateRuleRequest:
		logger.info("Validating the rule actions.")
		for action in request_body.actions:
			logger.info(f"Validating rule action. Action - {action.action} | Value - {action.value}")

			if action.action == ActionType.MOVE:
				if not action.value:
					error_msg = f"Move labels is required for action {action.action}"
					logger.error(error_msg)
					raise InvalidDataException(error_msg)

				labels = [label.strip() for label in action.value.split(",")]
				logger.info(f"Validating labels - {labels}")
				for label in labels:
					LabelService().get_label_by_name(label)

			elif action.action in [ActionType.MARK_AS_READ, ActionType.MARK_AS_UNREAD, ActionType.DELETE]:
				if action.value:
					error_msg = f"Value is not allowed for action {action.action}"
					logger.error(error_msg)
					raise InvalidDataException(error_msg)

			elif action.action == ActionType.FORWARD:
				error_msg = f"Email forwarding features is under development and not supported yet"
				logger.error(error_msg)
				raise InvalidDataException(error_msg)

			else:
				error_msg = f"Action {action.action} is not a valid action type"
				logger.error(error_msg)
				raise InvalidDataException(error_msg)

		logger.info("Rule actions validated successfully.")
		return request_body

	@staticmethod
	def _create_rule_in_db(request_body: CreateRuleRequest, filter_field_map: dict) -> Rule:
		logger.info("Creating the rule in the database.")
		rule_id = uuid4()
		rule_body = request_body.model_dump()
		rule_body["id"] = rule_id

		db_objects = []
		rule_details = []
		rule_actions = []
		rule = BaseRepo(Rule).create(rule_body, commit=False)
		db_objects.append(rule)

		for rule_detail in request_body.rule_details:
			rule_detail_body = rule_detail.model_dump()
			rule_detail_body["rule_id"] = rule_id
			rule_detail_body["filter_field_id"] = filter_field_map[rule_detail.field_name]
			rule_detail = BaseRepo(RuleDetail).create(rule_detail_body, commit=False)
			db_objects.append(rule_detail)
			rule_details.append(rule_detail)

		for action in request_body.actions:
			action_body = action.model_dump()
			action_body["rule_id"] = rule_id
			action = BaseRepo(RuleAction).create(action_body, commit=False)
			db_objects.append(action)
			rule_actions.append(action)

		logger.info("Trying to commit the rule to the database.")
		with SqlContext() as sql_context:
			sql_context.session.add_all(db_objects)

		rule.rule_details = rule_details
		rule.actions = rule_actions

		logger.info("Rule created successfully in the database.")
		return rule

	@staticmethod
	def create_rule(request_body: CreateRuleRequest) -> Rule:
		logger.info("Calling the Create rule service.")

		try:
			RuleService.get_rule_by_name(request_body.name)
		except RecordNotFoundError as ex:
			logger.info(
				f"Rule doesn't exist with rule name: {request_body.name}. Creating a new rule."
			)
		else:
			error_msg = f"Rule already exists with rule name: {request_body.name}"
			logger.error(error_msg)
			raise DuplicateRecordError(error_msg)

		request_body, filter_field_map = RuleService._validate_rule_details(request_body)
		request_body = RuleService._validate_rule_actions(request_body)
		rule = RuleService._create_rule_in_db(request_body, filter_field_map)

		return rule

	@staticmethod
	def _execute_rule(rule: Rule) -> [str]:
		logger.info("Executing the rule.")
		messages = MessageRepo().execute_rule(rule)
		logger.info(f"Messages found - {len(messages)}")
		return messages

	@staticmethod
	def _execute_actions(rule_actions: [RuleAction], messages: [Message]) -> None:
		logger.info("Executing the actions.")
		add_db_objs = []
		delete_db_objs = []

		for rule_action in rule_actions:
			logger.info(f"Executing action - {rule_action.action} | Value - {rule_action.value}")
			if rule_action.action == ActionType.MOVE:
				labels = [LabelService().get_label_by_name(label.strip())for label in rule_action.value.split(",")]
				for message in messages:
					message_labels = CommonService.get_record_by_col(
						BaseRepo(MessageLabel), "message_id", message.message_id
					)
					message_labels = message_labels if isinstance(message_labels, list) else [message_labels]
					delete_db_objs.extend(message_labels)
					for label in labels:
						message_label = BaseRepo(MessageLabel).create(
							{"message_id": message.message_id, "label_id": label.label_id}, commit=False
						)
						add_db_objs.append(message_label)

					from_label_ids = [label.label_id for label in message_labels]
					to_label_ids = [label.label_id for label in labels]
					GmailService().move_labels(message.message_id, from_label_ids, to_label_ids)

				with SqlContext() as sql_context:
					sql_context.session.add_all(add_db_objs)
					for obj in delete_db_objs:
						sql_context.session.delete(obj)

			elif rule_action.action in [ActionType.MARK_AS_READ, ActionType.MARK_AS_UNREAD]:
				from_label = LABEL_UNREAD if rule_action.action == ActionType.MARK_AS_READ else []
				to_label = [] if from_label == LABEL_UNREAD else LABEL_UNREAD
				for message in messages:
					message_label = MessageLabelRepo().get_message_label_by_message_and_label_id(
						from_label, message.message_id
					)
					if message_label:
						BaseRepo(MessageLabel).delete(message_label)

					MessageLabelService.create_message_label(message.message_id, to_label)
					GmailService().move_labels(message.message_id, [from_label], [to_label])

			elif rule_action.action == ActionType.DELETE:
				for message in messages:
					MessageService().deactivate_message(message.id)

	@staticmethod
	def execute_rule_by_id_or_name(
			rule_id: (str, UUID) = None, rule_name: str = None, execute_actions: bool = False
	) -> [Message]:
		logger.info("Executing the rule by rule name or rule id.")
		if rule_id:
			rule = RuleService.get_rule_by_id(rule_id, get_filter_field_detail=True)
		else:
			rule = RuleService.get_rule_by_name(rule_name, get_filter_field_detail=True)

		messages = RuleService._execute_rule(rule)
		if execute_actions:
			RuleService._execute_actions(rule.actions, messages)
		return messages

	@staticmethod
	def delete_rule(rule_id: (str, UUID)) -> None:
		logger.info("Deleting the rule.")
		rule = RuleService.get_rule_by_id(rule_id)
		for action in rule.actions:
			BaseRepo(RuleAction).delete(action)

		for detail in rule.rule_details:
			BaseRepo(RuleDetail).delete(detail)

		BaseRepo(Rule).delete(rule)

		logger.info("Rule deleted successfully.")
		return None
