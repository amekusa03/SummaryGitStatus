"""
Git repository scanner and status parser.
Provides functions to discover Git repositories in a directory tree and inspect their status.
"""

import os
import subprocess
from dataclasses import dataclass, asdict
from typing import List, Optional, Set
from concurrent.futures import ThreadPoolExecutor, as_completed

@dataclass
class RepoStatus:
    name: str
    path: str
    branch: str = "Unknown"
    upstream: Optional[str] = None
    ahead: int = 0
    behind: int = 0
    staged: int = 0
    unstaged: int = 0
    untracked: int = 0
    conflicts: int = 0
    stash_count: int = 0
    is_clean: bool = True
    last_commit_hash: str = ""
    last_commit_msg: str = ""
    last_commit_date: str = ""
    last_commit_author: str = ""
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


DEFAULT_EXCLUDE_DIRS = {
    "node_modules", ".venv", "venv", "__pycache__", 
    "target", "build", "dist", ".idea", ".vscode", "vendor", ".cache"
}


def find_git_repos(root_dir: str, max_depth: int = 4, exclude_dirs: Optional[Set[str]] = None) -> List[str]:
    """
    Recursively find all Git repository directories under root_dir up to max_depth.
    """
    if exclude_dirs is None:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS

    root_dir = os.path.abspath(root_dir)
    git_repo_paths = []

    if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
        return []

    # Check if root_dir itself is a git repo
    if os.path.exists(os.path.join(root_dir, ".git")):
        return [root_dir]

    root_depth = root_dir.rstrip(os.sep).count(os.sep)

    for current_dir, dirs, _ in os.walk(root_dir, topdown=True):
        cur_depth = current_dir.rstrip(os.sep).count(os.sep) - root_depth

        if ".git" in dirs:
            git_repo_paths.append(current_dir)
            dirs.clear()
            continue

        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        if cur_depth >= max_depth:
            dirs.clear()

    return sorted(git_repo_paths)


def get_repo_status(repo_path: str) -> RepoStatus:
    """
    Get detailed Git status of a single repository path.
    """
    repo_name = os.path.basename(os.path.normpath(repo_path))
    status = RepoStatus(name=repo_name, path=repo_path)

    if not os.path.isdir(repo_path):
        status.error = "Directory does not exist"
        return status

    # 1. Parse porcelain v2 status
    try:
        res = subprocess.run(
            ["git", "status", "--porcelain=v2", "-b"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode != 0:
            status.error = res.stderr.strip() or "Not a git repository"
            return status

        lines = res.stdout.splitlines()
        staged = 0
        unstaged = 0
        untracked = 0
        conflicts = 0

        for line in lines:
            if line.startswith("# branch.head "):
                status.branch = line.split(" ", 2)[2].strip()
                if status.branch == "(detached)":
                    status.branch = "HEAD (detached)"
            elif line.startswith("# branch.upstream "):
                status.upstream = line.split(" ", 2)[2].strip()
            elif line.startswith("# branch.ab "):
                parts = line.split()
                if len(parts) >= 4:
                    status.ahead = int(parts[2].lstrip("+"))
                    status.behind = int(parts[3].lstrip("-"))
            elif line.startswith("1 "):
                # Tracked entry
                parts = line.split()
                xy = parts[1]
                if xy[0] != '.':
                    staged += 1
                if xy[1] != '.':
                    unstaged += 1
            elif line.startswith("2 "):
                # Renamed / copied
                parts = line.split()
                xy = parts[1]
                if xy[0] != '.':
                    staged += 1
                if xy[1] != '.':
                    unstaged += 1
            elif line.startswith("u "):
                # Unmerged / conflict
                conflicts += 1
            elif line.startswith("? "):
                # Untracked
                untracked += 1

        status.staged = staged
        status.unstaged = unstaged
        status.untracked = untracked
        status.conflicts = conflicts
        status.is_clean = (staged == 0 and unstaged == 0 and untracked == 0 and conflicts == 0)

    except Exception as e:
        status.error = str(e)
        return status

    # 2. Get last commit details
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--format=%h%x09%an%x09%cr%x09%s"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode == 0 and res.stdout.strip():
            parts = res.stdout.strip().split("\t")
            if len(parts) >= 1: status.last_commit_hash = parts[0]
            if len(parts) >= 2: status.last_commit_author = parts[1]
            if len(parts) >= 3: status.last_commit_date = parts[2]
            if len(parts) >= 4: status.last_commit_msg = parts[3]
    except Exception:
        pass

    # 3. Get stash count
    try:
        res = subprocess.run(
            ["git", "stash", "list"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5,
            encoding="utf-8",
            errors="replace"
        )
        if res.returncode == 0 and res.stdout.strip():
            status.stash_count = len(res.stdout.strip().splitlines())
    except Exception:
        pass

    return status


def scan_repositories_multithreaded(
    root_dir: str, 
    max_depth: int = 4, 
    exclude_dirs: Optional[Set[str]] = None,
    progress_callback=None,
    max_workers: int = 8
) -> List[RepoStatus]:
    """
    Find and scan all git repos in parallel using ThreadPoolExecutor.
    Optional progress_callback(completed_count, total_count, current_status).
    """
    repo_paths = find_git_repos(root_dir, max_depth=max_depth, exclude_dirs=exclude_dirs)
    total = len(repo_paths)
    results = []

    if total == 0:
        return []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {executor.submit(get_repo_status, path): path for path in repo_paths}
        completed = 0
        for future in as_completed(future_to_path):
            completed += 1
            try:
                repo_status = future.result()
                results.append(repo_status)
                if progress_callback:
                    progress_callback(completed, total, repo_status)
            except Exception as e:
                path = future_to_path[future]
                err_status = RepoStatus(name=os.path.basename(path), path=path, error=str(e))
                results.append(err_status)
                if progress_callback:
                    progress_callback(completed, total, err_status)

    return sorted(results, key=lambda r: r.name.lower())
