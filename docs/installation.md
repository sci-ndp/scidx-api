# Installation

## Prerequisites

- Python 3.10 or higher
- virtualenv (optional but recommended)
- An instance of [CKAN](https://github.com/ckan/ckan-docker.git) installed and running. [Official documentation](https://docs.ckan.org/en/2.10/maintaining/installing/index.html).
- (Optional) An other instance of [CKAN](https://github.com/ckan/ckan-docker.git) installed and running, which works as the "global CKAN".
- An instance of [Keycloak](https://www.keycloak.org/) installed and running. We are using the docker [quay.io/keycloak/keycloak:25.0.1](https://www.keycloak.org/getting-started/getting-started-docker).

## Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/sci-ndp/scidx-api.git
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

4. Create a `env_variables` directory in the root of the project.

5. Create a `.env_ckan` file in the `env_variables` directory with the following content:
    ```env
    CKAN_URL=http://your-ckan-instance-url
    CKAN_API_KEY=your-ckan-api-key
    CKAN_GLOBAL_URL=http://global-ckan-instance-url
    ```

6. Create a `.env_swagger` file in the `env_variables` directory with the following content:
    ```env
    SWAGGER_TITLE=sciDX REST API
    SWAGGER_DESCRIPTION=API documentation
    SWAGGER_VERSION=0.1.0
    ```

7. Create a `.env_keycloak` file in the `env_variables` directory with the following content:
    ```env
    KEYCLOAK_URL=http://your-keycloak-instance-url
    KEYCLOAK_ADMIN_USERNAME=your-admin-username
    KEYCLOAK_ADMIN_PASSWORD=your-admin-password
    REALM_NAME=your-realm-name
    CLIENT_ID=your-client-id
    CLIENT_SECRET=your-client-secret

    ```

8. After finishing the installation and making sure everything is working please go to [configuration](../docs/configuration.md).

[Return to README.md](../README.md)