from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_host: str = ""
    kafka_port: str = ""
    kafka_prefix: str = ""

    model_config = {
        "env_file": "./env_variables/.env_kafka",
        "extra": "allow",
    }


kafka_settings = Settings()