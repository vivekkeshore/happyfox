# Define variables
PYTHON := python3
PIP := pip3

# Install dependencies
install:
	$(PIP) install pipenv
	pipenv install --skip-lock

# Run tests
test:
	pipenv run pytest tests

# Run the application
run:
	pipenv run $(PYTHON) main.py

gmail_cli:
	pipenv run $(PYTHON) gmail_utility.py fetch_emails $(ARGS)


# Help
help:
	@echo "Makefile for HappyFox assignment project"
	@echo "Usage:"
	@echo "  make install   - Install dependencies"
	@echo "  make test      - Run tests"
	@echo "  make run       - Run the application"
	@echo "  make help      - Show this help message"
	@echo "  make gmail_cli - Run the gmail utility"
