# EvalLens Test Suite

This directory contains automated test suites for EvalLens.

## Structure

```
TEST/
├── unit/           # Fast unit tests for settings, models, validators, and client logic
├── integration/    # Integration tests for database schema, migrations, and module imports
└── fixtures/       # Reusable test fixtures and temporary path providers
```

## Running the Tests

To run the entire test suite using pytest:

```bash
# Ensure your virtual environment is active
pytest TEST/
```

To run with verbose output:

```bash
pytest TEST/ -v
```

To run specific test categories:

```bash
pytest TEST/unit/ -v
pytest TEST/integration/ -v
```

