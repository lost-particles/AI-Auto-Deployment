# detector.py (Handles app type + provider detection + deployment generation + logging)
import os
import json
import re
import subprocess
import shutil
import google.generativeai as genai
from json.decoder import JSONDecodeError
from datetime import datetime
from credentials import get_credentials_for_provider, save_credentials_safely

CACHE_FILE = ".detector_strategy_cache.json"
DEPLOYMENT_DIR = "deployment_configs"
DEPLOYMENT_LOG = "deployment_steps.log"

model = genai.GenerativeModel("gemini-2.0-flash")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

SPLIT_TOKEN = "###==FILE==###"

def log_step(step: str):
    timestamp = datetime.utcnow().isoformat()
    with open(DEPLOYMENT_LOG, "a") as f:
        f.write(f"[{timestamp}] {step}\n")

def _collect_file_snippets(repo_path: str, filenames: list[str]) -> str:
    snippets = []
    for fname in filenames:
        full_path = os.path.join(repo_path, fname)
        if os.path.isfile(full_path):
            try:
                with open(full_path, "r") as f:
                    content = f.read(1000)
                    snippets.append(f"--- {fname} ---\n{content}\n")
            except Exception:
                continue
    return "\n".join(snippets)

def detect_app_type(file_list: list[str], description: str, repo_path: str, app_types: list[str] = None) -> str:
    config_preview = _collect_file_snippets(repo_path, ["requirements.txt", "README.md", "package.json", "Dockerfile"])
    prompt = f"""
Given the following project files:
{file_list}

And the description:
{description}

Here are snippets from key configuration files:
{config_preview}

What type of application is this?
Return only the app type as one lowercase word.
"""
    response = model.generate_content([prompt])
    raw = response.text.strip().lower()

    if not raw:
        log_step("Gemini returned empty app type.")
        raise ValueError("Gemini returned an empty response for app type detection.")

    log_step(f"Detected application type: {raw}")
    return raw

def recommend_cloud_provider(description: str, repo_path: str) -> str:
    config_preview = _collect_file_snippets(repo_path, ["requirements.txt", "README.md", "package.json", "Dockerfile"])
    prompt = f"""
Given the following application description:
{description}

Here are relevant configuration file contents:
{config_preview}

What is the best cloud provider to deploy this application?
Return only the provider name, lowercase.
"""
    response = model.generate_content([prompt])
    raw = response.text.strip().lower()

    if not raw or raw == 'any':
        log_step(f"Gemini returned invalid or generic provider: '{raw}'. Using default 'aws'.")
        raw = "aws"

    confirm = input(f"Gemini suggests using '{raw}' as the cloud provider. Do you want to use this? (y/n): ").strip().lower()
    if confirm != 'y':
        raw = input("Please enter your preferred cloud provider (in lowercase): ").strip().lower()

    log_step(f"Final cloud provider selected: {raw}")
    return raw

def extract_and_save_config_files(config_text: str, config_dir: str):
    parts = config_text.split(SPLIT_TOKEN)
    saved_paths = []
    for part in parts:
        lines = part.strip().splitlines()
        if len(lines) < 2:
            continue
        filename = lines[0].strip()
        content = "\n".join(lines[1:]).strip()
        if not filename:
            continue
        safe_filename = filename.replace("/", "_").replace(" ", "_").strip()
        filepath = os.path.join(config_dir, safe_filename)
        with open(filepath, "w") as f:
            f.write(content)
        saved_paths.append(filepath)
    if not saved_paths:
        fallback_path = os.path.join(config_dir, "main.tf")
        with open(fallback_path, "w") as f:
            f.write(config_text)
        saved_paths.append(fallback_path)
    return saved_paths

def generate_deployment_files(description: str, app_type: str, provider: str) -> str:
    os.makedirs(DEPLOYMENT_DIR, exist_ok=True)
    prompt = f"""
Given the application type '{app_type}' and cloud provider '{provider}', generate infrastructure as code (Terraform preferred, or native deployment config if Terraform is unsupported) that will deploy the application described below:

{description}

The generated configuration should include any infrastructure and provisioning steps required to make the application accessible publicly.

Output each file like this format:
{SPLIT_TOKEN}
<file_name.ext>
<file_content>
{SPLIT_TOKEN}

Only use this exact structure. Avoid extra commentary or markdown.
"""
    response = model.generate_content([prompt])
    config_text = response.text.strip()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    config_dir = os.path.join(DEPLOYMENT_DIR, f"{provider}_{timestamp}")
    os.makedirs(config_dir, exist_ok=True)

    saved_paths = extract_and_save_config_files(config_text, config_dir)

    log_step(f"Generated deployment config for {provider} saved at {config_dir}")
    print(f"[INFO] Deployment config saved to: {config_dir}")

    ask_creds = input("Do you want to deploy now? (y/n): ").strip().lower()
    if ask_creds == 'y':
        creds = get_credentials_for_provider(provider)
        save_credentials_safely(provider, creds)
        log_step("User opted for auto-deployment. Credentials captured.")

        try:
            if provider in ["aws", "gcp", "azure"]:
                subprocess.run(["terraform", "init"], cwd=config_dir, check=True)
                subprocess.run(["terraform", "apply", "-auto-approve"], cwd=config_dir, check=True)
                log_step("Terraform deployment successful.")
                print("[SUCCESS] Deployment completed successfully.")
            elif provider in ["vercel", "netlify", "railway"]:
                if shutil.which(provider) is None:
                    log_step(f"{provider} CLI not found in PATH.")
                    print(f"[ERROR] {provider} CLI is not installed or not in PATH.")
                else:
                    cmd = {
                        "vercel": ["vercel", "deploy", "--prod"],
                        "netlify": ["netlify", "deploy", "--prod"],
                        "railway": ["railway", "up"]
                    }[provider]
                    subprocess.run(cmd, cwd=config_dir, check=True)
                    log_step(f"{provider.capitalize()} deployment successful.")
            else:
                log_step(f"No auto-deploy command configured for provider: {provider}")
                print("[INFO] Manual deployment required for this provider.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Deployment command failed: {e}")
            log_step(f"Deployment failed: {e}")
    else:
        print("[INFO] Deployment skipped. You can use the generated files to deploy manually.")
        log_step("Deployment skipped by user.")

    return config_dir
