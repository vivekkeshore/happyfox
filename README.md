HappyFox Assignment
====================

### Overview
This projects implements 2 key functionalities.
1. `gmail_utility` - A CLI utility tool, that can fetch the emails from gmail apis and store in database.
2. `process_emails` - A CLI utility tool, that can fetch the emails from database, perform search, apply various rules & actions, and simultaneously update the emails in the gmail account as well.


### Requirements
- Python 3.10 and above
- Pipenv
- Postgres
- Gmail Account
- Google API Credentials


### DB ERD
View db ERD at https://dbdocs.io/vivekkeshore/HappyFoxAssignment


### Project Structure
- `gmail_utility.py`: CLI tool. Typer based CLI application for fetching and storing emails.
- `process_emails.py`: CLI tool, Typer based CLI application for processing emails based on rules and actions.
- `Makefile`: Makefile for managing tasks.
- `Pipfile`: Pipenv file for managing dependencies.
- `.env`: Environment variables file.
- `rules.json`: Contains the rules and actions to be applied on emails, in json format.
- `helpers` dir: Contains the helper functions.
  - `db_models.py`: Contains the SQLAlchemy based database models.
  - `enum_models.py`: Contains the Enum classes.
  - `field_rule.py`: Contains the field rules to be applied on emails.
  - `gmail_service.py`: A wrapper class over Gmail APIs.
  - `schema_models.py`: Contains the Pydantic models for Rule, Rule details and Actions objects.
  - db_helpers: Module containing the database helper functions.
    - `base_repo.py`: Base repository class for database operations.
    - `message_label_repo.py`: Repository class for MessageLabel model.
    - `message_repo.py`: Repository class for Message model.
    - `sql_context.py`: Contains the database session context manager.


### Installation
To create the pipenv env and install the dependencies, execute:

```sh
make install
```
#### Alternative to make command
```sh
pipenv shell
pipenv install
```

#### copy the .env.example to .env
```sh
cp .env.example .env
```

### Running Tests
To run the tests, execute:

```sh
make test
```
#### Alternative to make command
```sh
python -m pytest
```

### Setting up google api credentials
- Create a project in google cloud console.
- Enable the Gmail API.
- Create the credentials for the project.
- Download the credentials as json file and name it as 'credentials.json'.
- For more details instructions, refer to 
  - https://developers.google.com/gmail/api/guides
  - https://developers.google.com/workspace/guides/get-started
  - https://developers.google.com/workspace/guides/configure-oauth-consent


### Running the first CLI Utility - gmail_utility
The CLI utility tool is used to fetch the emails from database and store in database.
It has two functionalities, display_email and fetch_emails.
  - Fetch emails fetches the emails from the gmail account and stores in the database.
  - Display emails displays the emails content in cli.

*`The tool uses a rich console output including a live progress bar, and a layout to display the emails.`*

To run the CLI utility, execute:

```sh
make gmail_cli
```
#### Alternative to make command
```sh
python gmail_utility.py
```

### gmail_utility help commands
```sh
python gmail_utility.py --help

python gmail_utility.py fetch_emails --help

python gmail_utility.py display_emails --help
```


### Run gmail utility with arguments
```sh
python gmail_utility.py fetch_emails --no-of-emails=100 --save-db

python gmail_utility.py display_emails --email_message_id=<email_message_id_from_gmail>
```

### Running the second CLI Utility - process_emails
The CLI utility tool is used to fetch the emails from database, perform search, apply various rules & actions, and simultaneously update the emails in the gmail account as well.
It has four functionalities:
  - Add Rules: Add rules to the rules.json.
  - Remove Rules: Remove rules from the rules.json.
  - Validate Rules: Validate the rules in the rules.json.
  - Execute Rules: Execute the rules & actions on the emails in the database.

To run the CLI utility, execute:


#### gmail_utility help commands
```sh
python process_emails.py --help

python process_emails.py add_rules --help

python process_emails.py execute_rules --help

python process_emails.py remove_rules --help

python process_emails.py validate_rules --help
```


#### Run `add_rules` utility with arguments
Interactive prompt based utility to add rules to the rules.json file.
```sh
python process_emails.py add_rules  # Defaults to 1, add 1 rule.

# Pass value to arg --no-of-rules
python process_emails.py add_rules --no-of-rules=5
```

#### Run `remove_rules` utility with arguments
```sh
python process_emails.py remove_rules  "Rule Name 1" "Rule Name 2" "Rule Name 3"
```

#### Run `validate_rules` utility with arguments
```sh
python process_emails.py validate_rules
```

#### Run `execute_rules` utility with arguments
```sh
# Execute all rules
python process_emails.py execute_rules

# Execute specific rule
python process_emails.py execute_rules --rule-name="Rule Name 1"

# Execute specific rule but skip the actions
python process_emails.py execute_rules --rule-name="Rule Name 1" --no-execute-actions

```
