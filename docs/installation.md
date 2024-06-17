# Installation

## Prerequisites

- Python 3.10 or higher
- virtualenv (optional but recommended)
- An instance of CKAN (https://docs.ckan.org/) installed and running

## Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/scidx-api.git
    cd scidx-api
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env_ckan` file in the `env_variables` directory with the following content:
    ```env
    CKAN_URL=http://your-ckan-instance-url
    CKAN_API_KEY=your-ckan-api-key
    ```

5. Create a `.env_swagger` file in the `env_variables` directory with the following content:
    ```env
    SWAGGER_TITLE=sciDX REST API
    SWAGGER_DESCRIPTION=API documentation
    SWAGGER_VERSION=0.1.0
    ```

[Return to README.md](../README.md)