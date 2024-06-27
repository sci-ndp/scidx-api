# Configuration

## Environment Variables

The application uses environment variables for configuration. You need to create two `.env` files in the `env_variables` directory:

1. `.env_ckan`
2. `.env_swagger`

### .env_ckan

This file contains the configuration for connecting to your CKAN instance.

```
CKAN_URL=http://your-ckan-instance-url
CKAN_API_KEY=your-ckan-api-key
```

- `CKAN_URL`: The URL of your CKAN instance.
- `CKAN_API_KEY`: Your CKAN API key. "please see [here](https://docs.ckan.org/en/2.10/api/index.html#authentication-and-api-tokens) how to optain an api key
### .env_swagger

This file contains the configuration for Swagger documentation.

```
SWAGGER_TITLE=sciDX REST API
SWAGGER_DESCRIPTION=API documentation
SWAGGER_VERSION=0.1.0
```

- `SWAGGER_TITLE`: The title of your API documentation.
- `SWAGGER_DESCRIPTION`: The description of your API.
- `SWAGGER_VERSION`: The version of your API.

## Additional Configuration

- Ensure that your CKAN instance is running and accessible from the machine where the API is deployed.
- The CKAN API key must have the necessary permissions to create and manage datasets and organizations.

[Return to README.md](../README.md)
