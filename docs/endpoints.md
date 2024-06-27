# Endpoints

## Organization Endpoints

- **Create Organization**
  - **URL:** `/organization`
  - **Method:** `POST`
  - **Description:** Create a new organization in CKAN.
  - **Request Body:**

```json
{
    "name": "example_org",
    "title": "Example Organization",
    "description": "This is an example organization."
}
```
  - **Response:**

```json
{
    "id": "organization_id",
    "message": "Organization created successfully"
}
```

- **Delete Organization**
  - **URL:** `/organization/{org_name}`
  - **Method:** `DELETE`
  - **Description:** Delete an organization in CKAN by name.
  - **Response:**

```json
{
    "message": "Organization deleted successfully"
}
```

- **List Organizations**
  - **URL:** `/organization`
  - **Method:** `GET`
  - **Description:** List all organizations in CKAN.
  - **Response:**

```json
[
    "organization_1",
    "organization_2",
    ...
]
```

## Data Source Endpoints

- **Create Data Source**
  - **URL:** `/datasource`
  - **Method:** `POST`
  - **Description:** Create a new dataset and its associated resource in CKAN.
  - **Request Body:**
    
```json
{
    "dataset_name": "example_dataset",
    "dataset_title": "Example Dataset",
    "owner_org": "organization_id",
    "resource_url": "http://example.com/resource",
    "resource_name": "Example Resource",
    "dataset_description": "This is an example dataset.",
    "resource_description": "This is an example resource.",
    "resource_format": "CSV"
}
```

  - **Response:**
    
```json
{
    "id": "dataset_id",
    "message": "Dataset created successfully"
}
```

- **Search Data Source**
  - **URL:** `/datasource`
  - **Method:** `GET`
  - **Description:** Search datasets based on various parameters.
  - **Query Parameters:**
    - `dataset_name`: The name of the dataset.
    - `dataset_title`: The title of the dataset.
    - `owner_org`: The name of the organization that owns the dataset.
    - `resource_url`: The URL of the dataset resource.
    - `resource_name`: The name of the dataset resource.
    - `dataset_description`: The description of the dataset.
    - `resource_description`: The description of the dataset resource.
    - `resource_format`: The format of the dataset resource.
    - `search_term`: A term to search across all dataset fields.
  - **Response:**

```json
[
    {
    "id": "dataset_id",
    "name": "dataset_name",
    "title": "dataset_title",
    "owner_org": "organization_id",
    "description": "dataset_description",
    "resources": [
        {
        "id": "resource_id",
        "url": "http://example.com/resource",
        "name": "resource_name",
        "description": "resource_description",
        "format": "CSV"
        }
    ]
    },
    ...
]
```


## URL Endpoints

- **Create URL Resource**
  - **URL:** `/url`
  - **Method:** `POST`
  - **Description:** Add a URL resource to CKAN.
  - **Request Body:**
    
```json
{
    "resource_name": "example_resource",
    "resource_title": "Example Resource",
    "owner_org": "organization_id",
    "resource_url": "http://example.com/resource",
    "notes": "Resource created for testing."
}
```

  - **Response:**
    
```json
{
    "id": "resource_id",
    "message": "Resource created successfully"
}
```
## S3 Endpoints

- **Create URL Resource**
  - **URL:** `/s3`
  - **Method:** `POST`
  - **Description:** Add a URL resource to CKAN.
  - **Request Body:**
    
```json
{
    "resource_name": "example_resource",
    "resource_title": "Example Resource",
    "owner_org": "organization_id",
    "resource_url": "http://example.com/resource",
    "notes": "Resource created for testing."
}
```

  - **Response:**
    
```json
{
    "id": "resource_id",
    "message": "Resource created successfully"
}
```

## Status Endpoint

- **Check CKAN Status**
  - **URL:** `/status`
  - **Method:** `GET`
  - **Description:** Check if the CKAN instance is active.
  - **Response:**
    
```json
{
    "status": "active"
}
```

[Return to README.md](../README.md)
