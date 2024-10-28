import base64
import re
from os import path
from typing import Union
from zoneinfo import ZoneInfo

import typer
from dateutil import parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from rich import print
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from typing_extensions import Annotated

from app.db_layer import BaseRepo
from app.db_layer.sql_context import SqlContext
from app.models import Label, Message, MessageDetail, MessageLabel, MessageAttachment

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
# The file token.json stores the user's access and refresh tokens.
TOKEN_JSON_FILE = "token.json"
# The file credentials.json stores the client_id and client_secret.
CREDENTIAL_JSON_FILE = "credentials.json"
SELF_USER = "me"
IST_TIMEZONE = ZoneInfo('Asia/Kolkata')
LABEL_COL_MAP = {
	"id": "label_id",
	"name": "name",
	"type": "type_",
}
PLAIN_TEXT_MIME_TYPE = "text/plain"
HTML_MIME_TYPE = "text/html"
IGNORED_MIME_TYPES = {
    "text/x-amp-html",
}

fetch_gmail_app = typer.Typer(
	help="Fetches the user's Gmail emails and store in database.",
	rich_markup_mode="markdown"
)
console = Console()


def get_gmail_creds(token_json: str = TOKEN_JSON_FILE, credentials_json: str = CREDENTIAL_JSON_FILE) -> Credentials:
	"""
	Gets the Gmail credentials from the token.json file or creates a new one.

	Args:
		token_json (str): The file token.json stores the user's access and refresh tokens.
		credentials_json (str): The file credentials.json stores the client_id and client_secret.

	Returns:
		Credentials: The user's Gmail credentials.
	"""
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	if path.exists(token_json):
		creds = Credentials.from_authorized_user_file(token_json, SCOPES)
	# If there are no (valid) credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				credentials_json, SCOPES
			)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open(token_json, "w") as token:
			token.write(creds.to_json())

	return creds


def get_all_labels(service: build) -> list:
	"""
	Gets all the labels from the user's Gmail account.

	Args:
		service (build): The Gmail API service.

	Returns:
		list: List of labels.

	Raises:
		HttpError: An error occurred while fetching the labels.
	"""
	try:
		results = service.users().labels().list(userId=SELF_USER).execute()
	except HttpError as error:
		print(f"An error occurred: {error.reason}")
		raise error

	labels = results.get("labels", [])
	return labels


def save_gmail_labels(service: build):
	"""
	Saves the Gmail labels in the database.

	Args:
		service (build): The Gmail API service.
	"""
	labels = get_all_labels(service)
	print(
		Panel.fit(
			f"Extracted [bold blue]{len(labels)}[/bold blue] labels from Gmail account.",
			title="Labels"
		)
	)
	for label in labels:
		print(f"[bold blue]Label - [/bold blue]{label['name']} | [bold green]Type - [/bold green]{label['type']}")
		label_data = {
			LABEL_COL_MAP[col]: label[col] for col in LABEL_COL_MAP
		}
		repo = BaseRepo(Label)
		label = repo.get_by_col("label_id", label_data["label_id"])
		if not label:
			repo.create(label_data)


def get_message_ids(service: build, no_of_emails: int) -> list:
	"""
	Gets the message ids from the user's Gmail account.

	Args:
		service (build): The Gmail API service object (Resource).
		no_of_emails (int): Number of emails to fetch.

	Returns:
		list: List of message ids.

	Raises:
		HttpError: An error occurred while fetching the messages.
	"""
	message_ids = []
	total_fetched = 0
	page_token = None
	while total_fetched < no_of_emails:
		batch_size = min(100, no_of_emails - total_fetched)

		# Call the Gmail API
		try:
			results = service.users().messages().list(
				userId=SELF_USER, maxResults=batch_size, pageToken=page_token
			).execute()

		except HttpError as error:
			print(f"An error occurred: {error.reason}")
			raise error

		messages = results.get("messages", [])
		page_token = results.get("nextPageToken")

		if not messages:
			print("[bold red]Alert![/bold blue]No more messages found.")
			break

		total_fetched += len(messages)
		message_ids.extend(messages)
		print(
			Panel.fit(
				f"[bold blue]Fetched![/bold blue] [green]{total_fetched} emails [/green] :e-mail: :boom:",
				title="Emails"
			)
		)

	return message_ids


def extract_email_address(email_address: str) -> Union[str, list]:
	"""
	Extracts the email address(s) from the given string.

	Args:
		email_address (str): The email address from header.

	Returns:
		Union[str, list]: Returns the extracted email address or list of email addresses.
	"""
	extracted_email_addresses = []
	email_addresses = email_address.split(",")
	for email_address in email_addresses:
		match = re.search(r'<(.+?)>', email_address.strip())
		email_address = match.group(1) if match else email_address
		extracted_email_addresses.append(email_address)

	return extracted_email_addresses

def get_metadata_from_headers(headers: list) -> dict:
	"""
	Extracts the subject, from address and other metadata from the message headers.

	Args:
		headers (list): List of headers from the message payload.

	Returns:
		dict: Dictionary containing the metadata like subject and from address.
	"""
	metadata = {}
	for header in headers:
		if header["name"] == "Subject":
			metadata["subject"] = header["value"]
		elif header["name"] == "From":
			metadata["from_address"] = extract_email_address(header["value"])[0]
		elif header["name"] == "To":
			metadata["to"] = extract_email_address(header["value"])
		elif header["name"] == "Cc":
			metadata["cc"] = extract_email_address(header["value"])
		elif header["name"] == "Bcc":
			metadata["bcc"] = extract_email_address(header["value"])
		elif header["name"] == "Date":
			received_at = header["value"]
			received_at = parser.parse(received_at)
			received_at = received_at.astimezone(IST_TIMEZONE)
			metadata["received_at"] = received_at.isoformat()

	return metadata


def decode_message_body(encoded_body: str) -> str:
	"""
	Decodes the base64 encoded message body.

	Args:
		encoded_body (str): The base64 encoded message body.

	Returns:
		str: The decoded message body.
	"""
	decoded_bytes = base64.urlsafe_b64decode(encoded_body)
	return decoded_bytes.decode("utf-8")


def process_email_parts(email_parts):
	"""
	Processes the parts of a multipart email to separate the body and attachments.

	Args:
		email_parts (list): List of parts in the email.

	Returns:
		dict: Dictionary containing 'text_body', 'html_body', and 'attachments'.
	"""
	email_content = {
		"text_body": None,
		"html_body": None,
		"attachments": []
	}

	for part in email_parts:
		if "parts" in part:
			email_content.update(process_email_parts(part["parts"]))
		else:
			mime_type = part["mimeType"]
			if mime_type == PLAIN_TEXT_MIME_TYPE:
				email_content["text_body"] = decode_message_body(part["body"]["data"])
			elif mime_type == HTML_MIME_TYPE:
				email_content["html_body"] = decode_message_body(part["body"]["data"])
			elif mime_type not in IGNORED_MIME_TYPES:
				print(
					f"[bold red]Alert![/bold red] | Attachment found | "
					f"[bold blue]Mime Type - {mime_type}[/bold blue] | File name - {part['filename']}"
				)
				attachment = {
					"file_name": part["filename"],
					"mime_type": mime_type,
					"attachment_id": part["body"]["attachmentId"],
					"size": part["body"]["size"],
				}
				email_content["attachments"].append(attachment)

	return email_content


def save_message_to_db(message_id: str, metadata: dict, email: dict):
	"""
	Saves the email message and other components like message label, attachments in the database.

	Args:
		message_id (str): The message id of the email.
		metadata (dict): The metadata extracted from the email headers.
		email (dict): The email message
	"""
	email_content = process_email_parts(email["payload"].get("parts", []))
	db_objects = []
	message_repo = BaseRepo(Message)
	message = message_repo.get_by_col("message_id", message_id)

	# Do not save in db if message already exist in db.
	if message:
		print(
			"[bold red]Alert![/bold red] | [bold blue]Email Message ID - {message_id}[/bold blue] | "
			"Email already exists in database :floppy_disk:"
		)
		return

	# Save the email message in database.
	print(
		f":floppy_disk: [bold blue]Email Message ID - [/bold blue]{message_id} | "
		f"[bold green]Saving in database[/bold green] :floppy_disk:"
	)
	message = message_repo.create(metadata, commit=False)
	db_objects.append(message)
	message_detail_repo = BaseRepo(MessageDetail)
	message_detail = message_detail_repo.create(
		{
			"message_id": message_id,
			"text_body": email_content["text_body"],
			"html_body": email_content["html_body"],
		},
		commit=False
	)
	db_objects.append(message_detail)

	# Save the message labels in database.
	message_label_repo = BaseRepo(MessageLabel)
	attachment_repo = BaseRepo(MessageAttachment)
	for label_id in email["labelIds"]:
		label_data = {
			"label_id": label_id,
			"message_id": message_id
		}
		message_label = message_label_repo.create(label_data, commit=False)
		db_objects.append(message_label)

	for attachment_content in email_content["attachments"]:
		attachment_content["message_id"] = message_id
		attachment = attachment_repo.create(attachment_content, commit=False)
		db_objects.append(attachment)

	with SqlContext() as sql_context:
		sql_context.session.add_all(db_objects)


def fetch_email_details(service: build, message_id: str) -> (dict, dict):
	"""
	Fetches the email details like metadata, body, attachments etc from the Gmail API.

	Args:
		service (build): The Gmail API service object (Resource).
		message_id (str): The message id of the email.

	Returns:
		tuple: Tuple containing the metadata and email details.

	Raises:
		HttpError: An error occurred while fetching the email details.
	"""
	try:
		email = service.users().messages().get(
			userId=SELF_USER, id=message_id, format="full"
		).execute()
	except HttpError as error:
		print(f"[bold red]Error![/bold red] | [bold blue]Email Message ID - message_id[/bold blue] | {error.reason}")
		raise error

	metadata = get_metadata_from_headers(email["payload"]["headers"])

	return metadata, email


@fetch_gmail_app.command("fetch_emails")
def fetch_emails(
	no_of_emails: Annotated[int, typer.Option(help="Number of emails to fetch.", min=1)] = 1000,
	save_db: Annotated[bool, typer.Option(help="Save emails in database.")] = True,
	token_json: Annotated[str, typer.Option(help="Token file path.")] = TOKEN_JSON_FILE,
	credentials_json: Annotated[str, typer.Option(help="Credentials file path.")] = CREDENTIAL_JSON_FILE
):
	"""
	**Fetch** the email messages from Gmail. :sparkles:

	* The user's Gmail credentials are stored in token.json.

	* The client_id and client_secret are stored in credentials.json.

	* The user's Gmail messages are fetched and stored in database.
	"""
	creds = get_gmail_creds(token_json=token_json, credentials_json=credentials_json)
	service = build(serviceName="gmail", version="v1", credentials=creds)

	if save_db:
		save_gmail_labels(service)

	message_ids = get_message_ids(service, no_of_emails)

	progress = Progress(
		"{task.description}",
		SpinnerColumn(),
		BarColumn(),
		TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
	)
	overall_task = progress.add_task(f"Processing Emails (0/{len(message_ids)})", total=len(message_ids))
	panel = Panel.fit(progress, title="Email Processing Progress", border_style="green")

	with Live(panel, refresh_per_second=10):
		for i, message_id_dict in enumerate(message_ids, start=1):
			message_id = message_id_dict["id"]
			try:
				metadata, email = fetch_email_details(service, message_id)
			except HttpError as error:
				print(f"[bold red]Skipping ...[/bold red]")
				continue

			metadata["message_id"] = message_id
			metadata["thread_id"] = message_id_dict["threadId"]

			print(
				f"\n[bold blue]Email Message ID - [/bold blue]{message_id} | "
				f"[bold green]Subject - [/bold green]{metadata['subject']}"
			)
			if save_db:
				save_message_to_db(message_id, metadata, email)

			progress.update(overall_task, advance=1, description=f"Processing Emails ({i}/{len(message_ids)})")


@fetch_gmail_app.command("display_email")
def display_email(
	email_message_id: Annotated[str, typer.Argument(help="Email message id from Gmail.")],
	token_json: Annotated[str, typer.Option(help="Token file path.")] = TOKEN_JSON_FILE,
	credentials_json: Annotated[str, typer.Option(help="Credentials file path.")] = CREDENTIAL_JSON_FILE
):
	"""
	**Display** the email message details from Gmail. :sparkles:

	* The user's Gmail credentials are stored in token.json.

	* The client_id and client_secret are stored in credentials.json.

	* The email message details are fetched and displayed.
	"""
	creds = get_gmail_creds(token_json=token_json, credentials_json=credentials_json)
	service = build(serviceName="gmail", version="v1", credentials=creds)

	metadata, email = fetch_email_details(service, email_message_id)
	metadata["message_id"] = email_message_id
	metadata["thread_id"] = email["threadId"]
	email_content = process_email_parts(email["payload"].get("parts", []))

	layout = Layout(name="main")
	layout["main"].split_row(
		Layout(name="side"),
		Layout(name="body", ratio=2, minimum_size=60),
	)
	layout["side"].split(Layout(name="Metadata", ratio=2), Layout(name="Attachments"))

	# Display the email metadata.
	table = Table("Metadata", "Value", title="Email Metadata")
	for key, value in metadata.items():
		if isinstance(value, list):
			value = ", ".join(value)
		table.add_row(f"[bold blue]{key}[/bold blue]", value)
	layout["Metadata"].update(
		Panel(
			Align.center(
				table, vertical="middle"), border_style="green", highlight=True, title="Email Metadata"
		)
	)

	# Display the email text body.
	layout["body"].update(Panel(email_content["text_body"], border_style="green", title="Text Body"))

	# Display the email attachments.
	table = Table("File Name", "Size", "Mime Type", title="Email Attachments")
	for attachment in email_content["attachments"]:
		table.add_row(attachment["file_name"], str(attachment["size"]), attachment["mime_type"])
	layout["Attachments"].update(
		Panel(
			Align.center(table, vertical="middle"), border_style="green",
			highlight=True, title="Email Attachments"
		)
	)

	print(layout)


if __name__ == "__main__":
	try:
		fetch_gmail_app()
	except Exception as ex:
		import traceback
		traceback.print_exc()
		console.print_exception()
