from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    swagger_title: str = "API Documentation"
    swagger_description: str = "This is the API documentation."
    swagger_version: str = "0.1.0"

    
    class Config:
        env_file = "./env_variables/.env_swagger"
        extra = "allow"
    
swagger_settings = Settings()