"""
Utility functions for opening external tools (File Explorer, Terminal, VS Code)
and exporting status data to CSV/JSON.
"""

import os
import sys
import csv
import json
import subprocess
import shutil
from typing import List
from git_scanner import RepoStatus


def open_in_file_manager(path: str):
    """Open given folder path in system file manager."""
    if not os.path.exists(path):
        return
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def open_in_terminal(path: str):
    """Open given folder path in terminal application."""
    if not os.path.exists(path):
        return
    if sys.platform == "win32":
        subprocess.Popen(["cmd.exe", "/c", "start", "cmd"], cwd=path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-a", "Terminal", path])
    else:
        # Linux terminal fallback list
        terminals = [
            ["gnome-terminal", "--working-directory", path],
            ["konsole", "--workdir", path],
            ["xfce4-terminal", "--working-directory", path],
            ["alacritty", "--working-directory", path],
            ["kitty", "--directory", path],
            ["xterm", "-e", f"cd '{path}' && bash"]
        ]
        for term_cmd in terminals:
            if shutil.which(term_cmd[0]):
                subprocess.Popen(term_cmd)
                return
        # Fallback to xdg-open if no terminal binary matched directly
        subprocess.Popen(["xdg-open", path])


def open_in_vscode(path: str):
    """Open given folder path in VS Code."""
    if shutil.which("code"):
        subprocess.Popen(["code", path])
    else:
        # If 'code' binary is not in PATH, fallback to file manager
        open_in_file_manager(path)


def export_to_csv(repo_list: List[RepoStatus], file_path: str):
    """Export repo status list to CSV file."""
    fieldnames = [
        "name", "path", "branch", "upstream", "ahead", "behind",
        "staged", "unstaged", "untracked", "conflicts", "stash_count",
        "is_clean", "last_commit_hash", "last_commit_author", "last_commit_date", "last_commit_msg", "error"
    ]
    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for repo in repo_list:
            writer.writerow(repo.to_dict())


def export_to_json(repo_list: List[RepoStatus], file_path: str):
    """Export repo status list to JSON file."""
    data = [repo.to_dict() for repo in repo_list]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
