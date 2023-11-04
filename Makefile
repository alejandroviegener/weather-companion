SHELL := /bin/bash


# Target for running tests
test:
	@echo "Running tests..."
	poetry run pytest .

# Target for checking code formatting 
code-quality:
	@echo "Checking code formatting..."
	poetry run black --check .
	poetry run isort --profile black .

# Target for formatting code 
format:
	@echo "Formatting code..."
	poetry run black .
	poetry run isort --profile black .

# Add additional targets as needed...

# Special target for help
help:
	@echo	"make test     			- Run pytest"
	@echo	"make code-quality     		- Check code format"
	@echo	"make format   			- Format code"
	@echo	"make help     			- Show this message"
