# cli.py (Main CLI entrypoint for auto-deployment system)
import os
import tempfile
import click
from detector import detect_app_type, recommend_cloud_provider, generate_deployment_files
from repo_handler import clone_or_extract, list_repo_files

def log(msg):
    print(f"[INFO] {msg}")

@click.command()
@click.option('--desc', prompt="Describe your deployment", help="Natural language deployment request")
@click.option('--repo', prompt="GitHub URL or zip file", help="Link to GitHub or a local zip file")
@click.option('--refresh', is_flag=True, help="Force refresh suggestion (currently unused)")
def main(desc, repo, refresh):
    log("Cloning or extracting repository...")
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = clone_or_extract(repo, tmpdir)
        repo_files = list_repo_files(repo_path)

        log("Detecting application type...")
        app_type = detect_app_type(repo_files, desc, repo_path)
        log(f"Detected application type: {app_type}")

        log("Recommending cloud platform provider...")
        provider = recommend_cloud_provider(desc, repo_path)
        log(f"Final Selected Provider: {provider}")

        log("Generating deployment infrastructure configuration...")
        generate_deployment_files(desc, app_type, provider)

if __name__ == '__main__':
    main()
