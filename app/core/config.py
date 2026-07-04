from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    project_name: str = "StockSniper Process API"
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_username: str = Field(default="admin", alias="API_USERNAME")
    api_password: str = Field(default="secret123", alias="API_PASSWORD")
    api_token: str = Field(default="super-secret-token", alias="API_TOKEN")
    script_path: str = Field(default="./scripts/monitor.py", alias="SCRIPT_PATH")

    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    smtp_server: str = Field(default="smtp.gmail.com", alias="SMTP_SERVER")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(default="", alias="SMTP_USER")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    email_to: str = Field(default="", alias="EMAIL_TO")
    check_interval_seconds: int = Field(default=300, alias="CHECK_INTERVAL_SECONDS")

    class Config:
        env_file = ".env"

settings = Settings()
