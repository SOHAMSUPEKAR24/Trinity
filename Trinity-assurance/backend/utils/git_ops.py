import os
import subprocess
import logging

# Base folder where all repos are stored
CLONE_BASE_DIR = "./repos"
os.makedirs(CLONE_BASE_DIR, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def clone_or_pull_repo(repo_url: str) -> str:
    """
    Clone or pull a GitHub repo into ./repos, safely replacing hyphens for import compatibility.
    Returns the absolute local path to the repo.
    """
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    safe_repo_name = repo_name.replace("-", "_")
    repo_path = os.path.join(CLONE_BASE_DIR, safe_repo_name)

    try:
        if os.path.exists(repo_path):
            git_dir = os.path.join(repo_path, ".git")
            if not os.path.exists(git_dir):
                logger.warning(f"[GitOps] Invalid Git repo found. Cleaning and recloning: {repo_path}")
                subprocess.run(["rm", "-rf", repo_path], check=True)
            else:
                logger.info(f"[GitOps] Pulling latest changes: {safe_repo_name}")
                subprocess.run(["git", "-C", repo_path, "pull"], check=True)

        if not os.path.exists(repo_path):
            logger.info(f"[GitOps] Cloning new repo: {repo_url} → {safe_repo_name}")
            subprocess.run(["git", "clone", repo_url, repo_path], check=True)

    except subprocess.CalledProcessError as e:
        logger.error(f"[GitOps] ❌ Git operation failed: {e.stderr if e.stderr else str(e)}")
        raise RuntimeError(f"Git clone/pull failed for {repo_url}")

    return repo_path


def ensure_python_importable(repo_path: str):
    """
    Makes all directories within a repo Python-importable by adding __init__.py files.
    """
    for root, dirs, _ in os.walk(repo_path):
        for d in dirs:
            dir_path = os.path.join(root, d)
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                open(init_file, "w").close()
                logger.debug(f"[GitOps] __init__.py added at: {init_file}")


def get_repo_diff(repo_path: str, file_path: str = "") -> str:
    """
    Return the Git diff for a file or full repo between last two commits.
    """
    args = ["git", "-C", repo_path, "diff", "HEAD~1", "HEAD"]
    if file_path:
        args.append(file_path)

    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        logger.error(f"[GitOps] ❌ Diff failed: {e.stderr.decode('utf-8')}")
        return ""