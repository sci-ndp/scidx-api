from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    keycloak_url: str = "http://localhost:5000"
    realm_name: str = "test"
    client_id: str = "test"
    client_secret: str = "test"
    
    model_config = {
        "env_file": "./env_variables/.env_keycloak",
        "extra": "allow",
    }
    
keycloak_settings = Settings()