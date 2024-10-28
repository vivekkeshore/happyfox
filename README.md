HappyFox Assignment
====================

### Overview
This projects implements 2 key functionalities.
1. A CLI utility tool, that can fetch the emails from gmail apis and store in database.
2. A set of REST APIs, that can fetch the emails from database, perform search, apply various rules, and simultaneously update the emails in the gmail account as well.

The app is build in layered architecture, with FastAPI as the web framework, Postgres as the database, and SQLAlchemy as the ORM.
The code is designed to be reusable, modular, and testable. The use of adapter pattern for performing common operations like list, get, search, etc. makes the code more maintainable and scalable.
The use of common exception handler decorator along with managed custom exceptions reduces the boilerplate code and makes the code more readable and maintainable.

### Requirements
- Python 3.10 and above
- Pipenv
- Postgres
- Gmail Account
- Google API Credentials


### Project Structure
- `gmail_utility.py`: CLI tool. Typer based CLI application for fetching and storing emails.
- `main.py`: FastAPI app.
- tests folder: Test cases for the application.
- `Makefile`: Makefile for managing tasks.
- `Pipfile`: Pipenv file for managing dependencies.
- migrations folder: Alembic migrations for database schema.
  - `seed_db.py`: Seed script for populating the database.
- `config.py`: Configuration file for the application.
- .env: Environment variables file.
- app folder: FastAPI app folder.
  - `apis`: API endpoints.
  - `db_layer`: Database layer containing sqlalchemy based db queries.
  - `lib`: Utility functions.
  - `models`: Database models.
  - `schemas_models`: Pydantic schemas for validation and serialization.
  - `services`: Business logic layer.
- dbdocs folder: Database documentation in dbml format. View db ERD at https://dbdocs.io/vivekkeshore/HappyFoxAssignment

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

### Running Tests
To run the tests, execute:

```sh
make test
```
#### Alternative to make command
```sh
python -m pytest
```

### Running the CLI Utility
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

### Running the Application
To run the application, let's setup the project.
The project setup has two parts.
1. Setting up the google api credentials.
2. Setting up codebase and running the application.

### Setting up google api credentials
- Create a project in google cloud console.
- Enable the Gmail API.
- Create the credentials for the project.
- Download the credentials as json file and name it as 'credentials.json'.
- For more details instructions, refer to 
  - https://developers.google.com/gmail/api/guides
  - https://developers.google.com/workspace/guides/get-started
  - https://developers.google.com/workspace/guides/configure-oauth-consent


### Setting up codebase and running the application

#### set PYTHONPATH
```sh
cd happyfox
export PYTHONPATH=$(pwd)
```

#### copy the .env.example to .env
```sh
cp .env.example .env
```

#### Setup the database
- Create a database in postgres.
- Update the database config values in .env file.
- Run the migrations to create the database schema.

```sh
alembic upgrade head
```

- Seed the database with essential data.
```sh
python migrations/seed_db.py
```

#### Run the application
```sh
make run
```
#### Alternative to make command
```sh
python main.py
```