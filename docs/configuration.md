# Configuration

## Environment Variables

The application uses environment variables for configuration. You need to create three `.env` files in the `env_variables` directory:

1. `.env_ckan`
2. `.env_swagger`
3. `.env_keycloak`
4. `.env_dxspaces`

### .env_ckan

This file contains the configuration for connecting to your CKAN instance.

```
CKAN_URL=http://your-ckan-instance-url
CKAN_API_KEY=your-ckan-api-key
CKAN_GLOBAL_URL=http://global-ckan-instance-url
```

- `CKAN_URL`: The URL of your CKAN instance.
- `CKAN_API_KEY`: Your CKAN API key. "please see [here](https://docs.ckan.org/en/2.10/api/index.html#authentication-and-api-tokens) how to optain an api key
- `CKAN_GLOBAL_URL`: The URL of the global CKAN instance. If you do not have a global CKAN instance, you can use the same URL as `CKAN_URL`.

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

### .env_keycloak

This file contains the configuration for connecting to your Keycloak instance.

```
KEYCLOAK_URL=http://your-keycloak-instance-url
KEYCLOAK_ADMIN_USERNAME=your-admin-username
KEYCLOAK_ADMIN_PASSWORD=your-admin-password
REALM_NAME=your-realm-name
CLIENT_ID=your-client-id
CLIENT_SECRET=your-client-secret
```

- `KEYCLOAK_URL`: The URL of your Keycloak instance.
- `KEYCLOAK_ADMIN_USERNAME`: The username for the Keycloak admin.
- `KEYCLOAK_ADMIN_PASSWORD`: The password for the Keycloak admin.
- `REALM_NAME`: The name of your Keycloak realm.
- `CLIENT_ID`: The client ID for your application.
- `CLIENT_SECRET`: The client secret for your application.

### .env_dxspaces
This file contains the configuration for connecting to your DXSpaces instance.
```
DXSPACES_URL=http://your-dxspaces-instance-url
DXSPACES_REGISTRATION=all|<comma-separted list of source types>|none
```

- `DXSPACES_URL`: The URL of your DXSpaces instance.
- `DXSPACES_REGISTRATION`: Which classes registrations are propagated to DataSpaces.

## Additional Configuration

- Ensure that your CKAN and Keycloak instance is running and accessible from the machine where the API is deployed.
- The CKAN API key must have the necessary permissions to create and manage datasets and organizations.

Next step is [running the api](../docs/usage.md).

[Return to README.md](../README.md)
