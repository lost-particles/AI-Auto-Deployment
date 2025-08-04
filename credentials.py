# credentials.py
import os
import json
from getpass import getpass

CREDENTIALS_DIR = os.path.expanduser("~/.autodeploy_credentials")

def get_credentials_for_provider(provider: str) -> dict:
    print(f"[INPUT] Enter credentials for {provider.upper()}:")
    creds = {}

    if provider == "aws":
        creds["aws_access_key_id"] = getpass("AWS Access Key ID: ")
        creds["aws_secret_access_key"] = getpass("AWS Secret Access Key: ")
    elif provider == "gcp":
        creds["gcp_service_account_key"] = getpass("GCP Service Account JSON Key: ")
    elif provider == "azure":
        creds["client_id"] = getpass("Azure Client ID: ")
        creds["client_secret"] = getpass("Azure Client Secret: ")
        creds["tenant_id"] = getpass("Azure Tenant ID: ")
        creds["subscription_id"] = getpass("Azure Subscription ID: ")
    elif provider in ["vercel", "netlify", "railway"]:
        creds["api_token"] = getpass(f"{provider.capitalize()} API Token: ")
    else:
        key = getpass(f"Enter auth token or credentials for {provider}: ")
        creds["token"] = key

    return creds


def save_credentials_safely(provider: str, creds: dict) -> None:
    os.makedirs(CREDENTIALS_DIR, exist_ok=True)
    cred_file = os.path.join(CREDENTIALS_DIR, f"{provider}_credentials.json")

    with open(cred_file, "w") as f:
        json.dump(creds, f)

    os.chmod(cred_file, 0o600)  # Owner read/write only
    print(f"[INFO] Credentials saved securely for provider: {provider}")
