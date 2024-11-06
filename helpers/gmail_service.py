from pathlib import Path

from rich import print
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCRIPT_LOCATION = Path(__file__).resolve().parent
TOKEN_JSON_FILE = (SCRIPT_LOCATION / '../token.json').resolve()
CREDENTIAL_JSON_FILE = (SCRIPT_LOCATION / '../credentials.json').resolve()
SCOPES = [
	"https://www.googleapis.com/auth/gmail.modify",
	"https://www.googleapis.com/auth/gmail.readonly"
]
SELF_USER = "me"

class GmailService:
	def __init__(self):
		creds = self.get_gmail_creds()
		self.service = build(serviceName="gmail", version="v1", credentials=creds)

	@staticmethod
	def get_gmail_creds() -> Credentials:
		creds = None
		if TOKEN_JSON_FILE.exists():
			creds = Credentials.from_authorized_user_file(str(TOKEN_JSON_FILE), SCOPES)
		# If there are no (valid) credentials available, let the user log in.
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					str(CREDENTIAL_JSON_FILE), SCOPES
				)
				creds = flow.run_local_server(port=0)
			# Save the credentials for the next run
			with open(TOKEN_JSON_FILE, "w") as token:
				token.write(creds.to_json())

		return creds

	def move_labels(self, message_id, from_labels, to_labels, user_id=SELF_USER):
		print(f"[yellow]Moving labels from {from_labels} to {to_labels} for message {message_id}[/yellow]")
		request_body = {
			"addLabelIds": to_labels,
			"removeLabelIds": from_labels
		}
		message = self.service.users().messages().modify(
			userId=user_id, id=message_id, body=request_body
		).execute()

		print(f"[yellow]Labels moved successfully from {from_labels} to {to_labels} for message {message_id}[/yellow]")
		return message
