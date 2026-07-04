from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    project_name: str = "StockSniper Process API"
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_username: str = Field(default="admin", alias="API_USERNAME")
    api_password: str = Field(default="secret123", alias="API_PASSWORD")
    api_token: str = Field(default="super-secret-token", alias="API_TOKEN")
    script_path: str = Field(default="./scripts/dummy_script.py", alias="SCRIPT_PATH")

    class Config:
        env_file = ".env"

settings = Settings()
