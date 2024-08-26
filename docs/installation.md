## Installation

Follow these steps to install and set up the sciDX API on your local machine:

### Prerequisites

Make sure you have the following installed on your system:

- **Python 3.8+**
- **Docker** and **Docker Compose**(if you plan to use the Docker setup). 
- **Git**
- *CKAN*, we are using the [Docker Compose setup for CKAN](https://github.com/ckan/ckan-docker).
- *Keycloak*, we are using the [official Keycloak on Docker tutorial].(https://www.keycloak.org/getting-started/getting-started-docker), with the version ```quay.io/keycloak/keycloak:25.0.4```.

### Clone the Repository

Clone the sciDX API repository from GitHub:

```bash
git clone https://github.com/your-username/scidx-api.git
cd scidx-api
```

### Environment Configuration

1. Copy the example environment files and adjust the configuration as needed:

   ```bash
   cp ./env_variables/.env_ckan.example ./env_variables/.env_ckan
   cp ./env_variables/.env_keycloak.example ./env_variables/.env_keycloak
   cp ./env_variables/.env_swagger.example ./env_variables/.env_swagger

   ```

2. Edit the `.env` files to match your local environment or deployment needs.

### Install Dependencies

#### Option 1: Using Virtual Environment

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

#### Option 2: Using Docker

1. Build and start the Docker containers:

   ```bash
   docker-compose up --build
   ```

### Running the Application

Start the application using one of the following methods:

- **With Virtual Environment**:

  ```bash
  uvicorn api.main:app --reload
  ```

- **With Docker**:

  ```bash
  docker-compose up
  ```

### Accessing the API

Once the application is running, you can access the sciDX API at:

- **Local environment**: `http://127.0.0.1:8000`
- **Docker environment**: `http://localhost:8000`

Return to [README](../README.md).