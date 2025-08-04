# repo_handler.py
import os
import zipfile
import tempfile
import requests
from git import Repo

def clone_or_extract(repo_url: str, tmp_dir: str) -> str:
    """Clones a git repo or extracts a zip file into tmp_dir, returns code path."""
    if repo_url.endswith(".zip"):
        zip_path = os.path.join(tmp_dir, "repo.zip")
        with open(zip_path, "wb") as f:
            f.write(requests.get(repo_url).content)
        extract_path = os.path.join(tmp_dir, "extracted")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
        return extract_path
    else:
        clone_path = os.path.join(tmp_dir, "repo")
        Repo.clone_from(repo_url, clone_path)
        return clone_path

def list_repo_files(path: str) -> list[str]:
    """Returns list of all files in the repo path (relative paths)."""
    files = []
    for root, _, filenames in os.walk(path):
        for name in filenames:
            files.append(os.path.relpath(os.path.join(root, name), path))
    return files
