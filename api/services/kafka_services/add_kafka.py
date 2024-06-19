# api/services/datasource_services.py
from api.config.ckan_settings import ckan_settings

def add_kafka(dataset_name, dataset_title, owner_org, kafka_topic, kafka_host, kafka_port, dataset_description):
    """
    Add a Kafka topic and its associated metadata to the system.

    Parameters
    ----------
    dataset_name : str
        The name of the dataset to be created.
    dataset_title : str
        The title of the dataset to be created.
    owner_org : str
        The ID of the organization to which the dataset belongs.
    kafka_topic : str
        The Kafka topic name.
    kafka_host : str
        The Kafka host.
    kafka_port : str
        The Kafka port.
    dataset_description : str, optional
        A description of the dataset (default is an empty string).

    Returns
    -------
    str
        The ID of the created dataset if successful.

    Raises
    ------
    Exception
        If there is an error creating the dataset or adding the resource, an
        exception is raised with a detailed message.
    """
    
    ckan = ckan_settings.ckan

    try:
        # Try to create the dataset in CKAN
        dataset = ckan.action.package_create(
            name=dataset_name,
            title=dataset_title,
            owner_org=owner_org,
            notes=dataset_description
        )
        # Retrieve the dataset ID
        dataset_id = dataset['id']
    except Exception as e:
        # If an error occurs, raise an exception with a detailed error message
        raise Exception(f"Error creating Kafka dataset: {str(e)}")
    
    if dataset_id:
        try:
            # Try to create the resource within the newly created dataset
            ckan.action.resource_create(
                package_id=dataset_id,
                url=f"{kafka_host}:{kafka_port}:{kafka_topic}",
                name=kafka_topic,
                description=f"Kafka topic {kafka_topic} hosted at {kafka_host}:{kafka_port}",
                format="Kafka"
            )
        except Exception as e:
            # If an error occurs, raise an exception with a detailed error message
            raise Exception(f"Error creating Kafka resource: {str(e)}")
        
        # If everything goes well, return the dataset ID
        return dataset_id
    else:
        # This shouldn't happen as the dataset creation should either succeed or raise an exception
        raise Exception("Unknown error occurred")
