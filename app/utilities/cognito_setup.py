from pydantic_settings import BaseSettings
from pydantic.types import Any
import os
from fastapi_cognito import CognitoAuth, CognitoSettings
class Settings(BaseSettings):
    check_expiration: bool = True
    jwt_header_prefix: str = "Bearer"
    jwt_header_name: str = "Authorization"
    userpools: dict[str, dict[str, Any]] = {
        "eu": {
            "region": "eu-west-2",
            "userpool_id": "",
            "app_client_id": [""] # Example with multiple ids
        },
        # "us": {
        #     "region": "USERPOOL_REGION",
        #     "userpool_id": "USERPOOL_ID",
        #     "app_client_id": "APP_CLIENT_ID"
        # },
        
    }

settings = Settings()

cognito_eu = CognitoAuth(
    settings = CognitoSettings.from_global_settings(settings)
)