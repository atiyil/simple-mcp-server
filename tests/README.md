# Test Suite

This directory contains the comprehensive test suite for the simple-mcp-server project.

## Test Organization

### Unit Tests
- **`test_config.py`**: Tests for configuration loading and management
  - Environment variable loading
  - Config file parsing (plain and key=value formats)
  - Error handling for missing/empty API keys
  - Configuration precedence

- **`test_perplexity_client.py`**: Tests for Perplexity API client
  - Client initialization
  - Query methods with various parameters
  - HTTP error handling
  - Response parsing
  - Health check functionality

### Medium Tests
- **`test_mcp_handlers.py`**: Tests for MCP protocol handlers
  - Tool registration and schemas
  - Tool execution (query_perplexity, search_perplexity)
  - Resource management
  - Prompt templates
  - Error handling and edge cases

### Integration Tests
- **`test_integration.py`**: End-to-end workflow tests
  - Complete request/response flows
  - Config → Client → Server integration
  - Multiple sequential queries
  - Different model selections
  - Error recovery workflows
  - Prompt → Tool execution workflows

## Running Tests

### Install Test Dependencies
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/test_config.py tests/test_perplexity_client.py

# Medium tests only
pytest tests/test_mcp_handlers.py

# Integration tests only
pytest tests/test_integration.py
```

### Run Tests with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Specific Test
```bash
pytest tests/test_config.py::TestConfig::test_init_with_env_variable
```

## Optional Real API Testing

Integration tests include an optional real API test that is disabled by default. To enable:

```bash
# Set environment variables
export TEST_USE_REAL_API=true
export PERPLEXITY_API_KEY=your_actual_key_here

# Run tests
pytest tests/test_integration.py
```

**Note**: Real API tests will consume API credits and should only be used for verification purposes.

## Test Structure

All tests follow these principles:
- **Isolation**: Unit tests mock external dependencies
- **Independence**: Tests can run in any order
- **Clarity**: Test names clearly describe what is being tested
- **Coverage**: Tests cover both success paths and error cases
- **Speed**: Unit tests are fast; integration tests may be slower

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- All tests use mocks by default (no real API calls required)
- Fast execution time
- Clear pass/fail indicators
- Detailed error messages on failure
