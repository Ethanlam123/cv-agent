# CV Agent Makefile

.PHONY: help install test test-unit test-integration test-coverage lint format clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install        Install dependencies"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo "  lint           Run linting"
	@echo "  format         Format code"
	@echo "  clean          Clean temporary files"

# Install dependencies
install:
	uv sync --extra test

# Run all tests
test:
	pytest

# Run unit tests only
test-unit:
	pytest tests/unit/ -m "not slow"

# Run integration tests
test-integration:
	pytest tests/test_main.py -m integration

# Run tests with coverage
test-coverage:
	pytest --cov=src/cv_agent --cov-report=html --cov-report=term

# Run linting (if available)
lint:
	@echo "Linting not configured yet"

# Format code (if available)
format:
	@echo "Code formatting not configured yet"

# Clean temporary files
clean:
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete