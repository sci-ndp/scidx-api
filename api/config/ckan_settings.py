from pydantic_settings import BaseSettings
from ckanapi import RemoteCKAN

class Settings(BaseSettings):
    ckan_url: str = "http://localhost:5000"
    ckan_api_key: str = "your-api-key"

    @property
    def ckan(self):
        return RemoteCKAN(self.ckan_url, apikey=self.ckan_api_key)

    class Config:
        env_file = "./env_variables/.env_ckan"
        extra = "allow"
    
ckan_settings = Settings()