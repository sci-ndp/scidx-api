from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_host: str = ""
    kafka_port: str = ""
    kafka_prefix: str = ""
    max_streams: int = 20

    model_config = {
        "env_file": "./env_variables/.env_kafka",
        "extra": "allow",
    }


kafka_settings = Settings()