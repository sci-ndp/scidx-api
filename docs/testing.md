# Testing

This document explains how to run the tests for the sciDX API.

## Requirements

Make sure you have the following installed:
- Python 3.10 or higher
- pytest

## Running the Tests

1. Install the required dependencies if you haven't already:

```bash
pip install -r requirements.txt
```

2. Make sure your CKAN instance is running and properly configured in the `.env_ckan` file.

3. To run the tests, use the following command:

```bash
pytest tests/
```

4. The tests will automatically create and delete test organizations and datasets in your CKAN instance. Ensure that no critical data is stored in the CKAN instance used for testing.

## Example Test Output

Here's an example output of a successful test run:

```bash
========================================================================== test session starts ==========================================================================
platform linux -- Python 3.10.12, pytest-8.2.1, pluggy-1.5.0
rootdir: /path/to/scidx-api
plugins: anyio-4.4.0, order-1.2.1
collected 5 items

tests/test_full_api_flow.py .....

====================================================================== 5 passed in 1.23s ======================================================================
```

## Additional Information

For more detailed information about the tests, refer to the individual test files in the `tests/` directory.

[Return to README.md](../README.md)
