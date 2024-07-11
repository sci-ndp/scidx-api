# Usage

## Running the sciDX API

### Using Command Line

1. Run the FastAPI application:
    ```bash
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
    ```
    Note: If you are using the API internally and don't want to expose it publicly, use this instead:
    ```bash
    uvicorn api.main:app --reload
    ```

2. Open your browser and navigate to `http://server-ip:8000/docs` to access the interactive API documentation provided by Swagger UI.

### Using Docker

In addition to using the command line, you can also run the FastAPI application using Docker. This method is recommended if you want a consistent environment or are deploying the application.

1. Ensure Docker is installed and running on your machine.

2. Navigate to the root directory of the repository where the Dockerfile is located.

3. Build the Docker image:
    ```bash
    docker build -t scidx-api .
    ```

4. Run the Docker container:
    ```bash
    docker run -d -p 8000:8000 scidx-api
    ```

5. Open your browser and navigate to `http://server-ip:8000/docs` to access the interactive API documentation provided by Swagger UI.

## Additional Notes

- Using the command line method is recommended when developing new code, as it allows for quicker iterations and debugging.
- The Docker method provides a consistent and isolated environment, which can be beneficial for deployment or when working in different environments.

[Return to README.md](../README.md)