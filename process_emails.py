import json
from typing import List, Optional

import typer
from googleapiclient.errors import HttpError
from pydantic import ValidationError
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from typing_extensions import Annotated

from helpers.db_helpers.base_repo import BaseRepo
from helpers.db_helpers.message_label_repo import MessageLabelRepo
from helpers.db_helpers.message_repo import MessageRepo
from helpers.db_helpers.sql_context import SqlContext
from helpers.db_models import Message, Label, MessageLabel
from helpers.enum_models import RulePredicate, FieldUnit, ActionType, FieldType
from helpers.field_rule import FIELD_RULE
from helpers.gmail_service import GmailService
from helpers.schema_models import CreateRuleDetailRequest, CreateRuleActionRequest, CreateRuleRequest

# Rules json file.
RULES_JSON_FILE = "rules.json"

# Constants.
LABEL_TRASH = "TRASH"
LABEL_INBOX = "INBOX"
LABEL_READ = "READ"
LABEL_UNREAD = "UNREAD"

process_email_app = typer.Typer(
	help="Process emails from Gmail based on defined rules and action.",
	rich_markup_mode="markdown"
)
console = Console()


def _get_rules(rule_json_file: str = RULES_JSON_FILE):
	"""
	Get rules from the rules json file.

	Args:
		rule_json_file (str): Rules json file.

	Returns:
		dict: Rules.
	"""
	with open(RULES_JSON_FILE, "r") as rule_file:
		rules = rule_file.read()
		rules = json.loads(rules) if rules else {}

	return rules

def _add_rule_actions(rule_name: str) -> List[dict]:
	"""
	Add actions for the rule.

	Args:
		rule_name (str): Rule name.

	Returns:
		List[dict]: List of actions.
	"""
	actions = []
	while True:
		action = Prompt.ask(
			f":dart: [green_yellow]Enter action for rule {rule_name}[/green_yellow]",
			choices=ActionType.values(), case_sensitive=False,
			show_choices=True
		).upper()

		value = None
		if action == ActionType.MOVE.value:
			value = Prompt.ask(f"[green_yellow]Enter comma separated value for action {action}[/green_yellow]")

		action = CreateRuleActionRequest(
			action=action,
			value=value
		)
		actions.append(action.model_dump())

		if typer.confirm("Do you want to add more actions?"):
			continue
		break

	return actions

def _add_rule_details(rule_name: str) -> List[dict]:
	"""
	Add rule details for the rule.

	Args:
		rule_name (str): Rule name.

	Returns:
		List[dict]: List of rule details.
	"""
	rules = []
	while True:
		field_name = Prompt.ask(
			f":white_check_mark: [sky_blue1] Enter field name for rule {rule_name}[/sky_blue1]",
			choices=list(FIELD_RULE.keys()), case_sensitive=False,
			show_choices=True
		).lower()

		allowed_operations = [op.name for op in FIELD_RULE[field_name]["allowed_operations"]]
		operation = Prompt.ask(
			f"[sky_blue1]Enter operation for field {field_name}[/sky_blue1]",
			choices=allowed_operations, case_sensitive=False,
			show_choices=True
		).upper()

		value = Prompt.ask(f"[sky_blue1]Enter value for field {field_name}[/sky_blue1]")
		if FIELD_RULE[field_name]["field_type"] == FieldType.NUMBER:
			if not value.isdigit():
				raise typer.BadParameter(f"Value {value} is not a valid number for field {field_name}")

		elif FIELD_RULE[field_name]["field_type"] == FieldType.BOOLEAN:
			if value.lower() not in ["true", "false"]:
				raise typer.BadParameter(f"Value {value} is not a valid boolean (true/false) for field {field_name}")

		unit = None
		if field_name == "received_at":
			unit = Prompt.ask(
				f"[sky_blue1]Enter unit for field {field_name}[/sky_blue1]",
				choices=FieldUnit.values(), case_sensitive=False,
				show_choices=True
			).upper()

		rule = CreateRuleDetailRequest(
			field_name=field_name,
			operation=operation,
			value=value,
			unit=unit
		)
		rules.append(rule.model_dump())

		if typer.confirm("Do you want to add more rule details?"):
			continue
		break

	return rules


@process_email_app.command("add_rules")
def add_rules(
	no_of_rules: Annotated[int, typer.Option(help="Number of rules to add.", min=1)] = 1,
	rule_json_file: Annotated[str, typer.Option(help="Rules json file.")] = RULES_JSON_FILE
):
	"""
	**Add Rule(s)** - Add rules to the rules json file.

	* **no_of_rules**: Number of rules to add.

	* **rule_json_file**: Rules json file.

	* **Example**: python process_emails.py add_rules --no-of-rules 2

	* Performs the validation of rules and action.
	"""
	rules = _get_rules(rule_json_file)

	for i in range(no_of_rules):
		print(f":boom: :white_check_mark: [bold blue] Creating Rule {i+1} :white_check_mark: :boom:")
		rule_name = Prompt.ask(f"[green]Enter rule name for rule {i+1}[/green]")
		if rule_name in rules:
			print(f"[bold red]Alert![/bold red] Overwriting existing rule - {rule_name}.\n")

		predicate = Prompt.ask(
			f"[green]Enter rule predicate for {rule_name}[/green]",
			choices=RulePredicate.values(),
			case_sensitive=False,
			show_choices=True
		).upper()
		rule_details = _add_rule_details(rule_name)
		actions = _add_rule_actions(rule_name)

		rule = CreateRuleRequest(
			name=rule_name,
			predicate=predicate,
			rule_details=rule_details,
			actions=actions
		)
		rules[rule_name] = rule.model_dump()

	with open(RULES_JSON_FILE, "w") as rule_file:
		rule_file.write(json.dumps(rules, indent=2))

	print(f":boom: :boom: :boom: [bold blue]Rules added successfully to {RULES_JSON_FILE}[/bold blue] :boom: :boom: :boom:")


@process_email_app.command("remove_rules")
def remove_rules(
	rule_names: Annotated[List[str], typer.Argument(help="Rule names to remove.")],
	rule_json_file: Annotated[str, typer.Option(help="Rules json file.")] = RULES_JSON_FILE
):
	"""
	**Remove Rule** - Remove rule from the rules json file.

	* **rule_names**: Rule names to remove.

	* **rule_json_file**: Rules json file.

	* **Example**: python process_emails.py remove_rules "Rule 1" "Rule 2" "Rule 3"
	"""
	rules = _get_rules(rule_json_file)

	for rule_name in rule_names:
		if rule_name not in rules:
			print(f"[bold red]Alert![/bold red] Rule {rule_name} does not exist.")
			continue
		print(f":boom: :white_check_mark: [bold blue] Removing rule {rule_name} :white_check_mark: :boom:")
		del rules[rule_name]

	with open(RULES_JSON_FILE, "w") as rule_file:
		rule_file.write(json.dumps(rules, indent=2))


@process_email_app.command("validate_rules")
def validate_rules(
	rule_json_file: Annotated[str, typer.Option(help="Rules json file.")] = RULES_JSON_FILE
):
	"""
	**Validate Rule(s)** - Validate rules from the rules json file.

	* **rule_json_file**: Rules json file.

	* **Example**: python process_emails.py validate_rules
	"""
	rules = _get_rules(rule_json_file)
	for rule_name, rule_data in rules.items():
		print(f":boom: :white_check_mark: [bold blue] Validating rule {rule_name} :white_check_mark: :boom:")
		try:
			CreateRuleRequest.model_validate(rule_data)
		except ValidationError as ex:
			print(f"[bold orange1]Rule {rule_name} validation failed.[/bold orange1]")
			print(f"[bold red]Error: {ex}[/bold red]")
			continue

		print(f"[bold green]Rule {rule_name} validated successfully.[/bold green]\n")


def _create_message_label(message_id: str, label_id: str):
	if not label_id:
		return

	message_label = MessageLabelRepo().get_message_label_by_message_and_label_id(label_id, message_id)
	if message_label:
		print(f"Message label already exists with message id: {message_label.message_id} and label id: {label_id}")
		return

	BaseRepo(MessageLabel).create({"message_id": message_id, "label_id": label_id})
	print(f"Message label created successfully with message id: {message_id} and label id: {label_id}")


def _move_to_trash(message_id: str):
	GmailService().move_labels(message_id, [LABEL_INBOX], [LABEL_TRASH])
	message_label = MessageLabelRepo().get_message_label_by_message_and_label_id(LABEL_INBOX, message_id)
	if message_label:
		print(f"Deleting message label with message id: {message_label.message_id} and label id: {LABEL_INBOX}")
		BaseRepo(MessageLabel).delete(message_label)

	_create_message_label(message_id, LABEL_TRASH)


def _execute_rule(rule: CreateRuleRequest) -> [Message]:
	messages = MessageRepo().execute_rule(rule)
	print(f":e-mail:  :e-mail:  [bold green]Messages found - {len(messages)}[/bold green]  :e-mail:  :e-mail:")
	return messages


def _execute_actions(rule_actions: [CreateRuleActionRequest], messages: [Message]) -> None:
	print(f"\n:dart: [bold green_yellow] Executing actions [/bold green_yellow]:dart:")
	add_db_objs = []
	delete_db_objs = []

	label_repo = BaseRepo(Label)
	message_label_repo = MessageLabelRepo()
	gmail_service = GmailService()

	for rule_action in rule_actions:
		print(f"\n:dart: [green_yellow]Executing Action - {rule_action.action} | Value - {rule_action.value} [/green_yellow]")
		if rule_action.action == ActionType.MOVE:
			labels = [label_repo.get_by_col("name", label.strip()) for label in rule_action.value.split(",")]
			for message in messages:
				message_labels = message_label_repo.get_by_col("message_id", message.message_id)
				message_labels = message_labels if isinstance(message_labels, list) else [message_labels]
				delete_db_objs.extend(message_labels)
				for label in labels:
					message_label = message_label_repo.create(
						{"message_id": message.message_id, "label_id": label.label_id}, commit=False
					)
					add_db_objs.append(message_label)

				from_label_ids = [label.label_id for label in message_labels]
				to_label_ids = [label.label_id for label in labels]
				gmail_service.move_labels(message.message_id, from_label_ids, to_label_ids)

			with SqlContext() as sql_context:
				sql_context.session.add_all(add_db_objs)
				for obj in delete_db_objs:
					sql_context.session.delete(obj)

		elif rule_action.action in [ActionType.MARK_AS_READ, ActionType.MARK_AS_UNREAD]:
			from_label = LABEL_UNREAD if rule_action.action == ActionType.MARK_AS_READ else []
			to_label = [] if from_label == LABEL_UNREAD else LABEL_UNREAD
			for message in messages:
				gmail_service.move_labels(message.message_id, [from_label], [to_label])

				message_label = message_label_repo.get_message_label_by_message_and_label_id(
					from_label, message.message_id
				)
				if message_label:
					message_label_repo.delete(message_label)
				_create_message_label(message.message_id, to_label)

		elif rule_action.action == ActionType.DELETE:
			for message in messages:
				_move_to_trash(message.id)


@process_email_app.command("execute_rules")
def execute_rules(
	rule_name: Annotated[Optional[str], typer.Option(help="Rule name to execute.")] = None,
	rule_json_file: Annotated[str, typer.Option(help="Rules json file.")] = RULES_JSON_FILE,
	execute_actions: Annotated[Optional[bool], typer.Option(help="Execute actions for the rule.")] = True
):
	"""
	**Execute Rule(s)** - Execute rules from the rules json file.

	* **rule_json_file**: Rules json file.

	* **Example**: python process_emails.py execute_rules

	* **Example**: python process_emails.py execute_rules --rule-name "Rule 1"
	"""
	rules = _get_rules(rule_json_file)
	if rule_name:
		if rule_name in rules:
			rules = {rule_name: rules[rule_name]}
		else:
			print(f"[bold red]Alert![/bold red] Invalid Rule. {rule_name} does not exist.")
			return

	for rule_name, rule_data in rules.items():
		print(f":boom: :white_check_mark: [bold sky_blue1] Executing rule {rule_name} [/bold sky_blue1] :white_check_mark: :boom:")
		try:
			rule = CreateRuleRequest(**rule_data)
			messages = _execute_rule(rule)
			for message in messages:
				print(
					f"\n[bold blue]Email Message ID - [/bold blue]{message.message_id} | "
					f"[bold green]From - [/bold green]{message.from_address} | "
					f"[bold green]Subject - [/bold green]{message.subject}"
				)

			if execute_actions:
				_execute_actions(rule.actions, messages)

			print(f"\n:boom: [bold sky_blue1]Rule {rule_name} executed successfully.[/bold sky_blue1] :boom:\n")
		except ValidationError as ex:
			print(f"[bold orange1]Rule {rule_name} execution failed.[/bold orange1]")
			print(f"[bold red]Error: {ex}[/bold red]")
			continue


if __name__ == "__main__":
	try:
		process_email_app()
	except HttpError as ex:
		print(f"[bold red]Error - Alert![/bold red] Invalid Operation: {ex.reason}")
	except Exception as ex:
		console.print_exception()
