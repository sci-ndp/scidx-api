from pydantic_settings import BaseSettings
from ckanapi import RemoteCKAN

class Settings(BaseSettings):
    keycloak_url: str = "http://localhost:5000"
    realm_name: str = "test"
    client_id: str = "test"
    client_secret: str = "test"
    test_username: str = "test"
    test_password: str = "test"
    test_token: str = "test"
    keycloak_admin_username: str = "admin"
    keycloak_admin_password: str = "admin"

    model_config = {
        "env_file": "./env_variables/.env_keycloak",
        "extra": "allow",
    }
    
keycloak_settings = Settings()