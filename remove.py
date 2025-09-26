#!/usr/bin/env python3
import os
import re
import tempfile
import shutil
import subprocess
import argparse
from pathlib import Path
import getpass

# Known patterns for common languages
COMMENT_PATTERNS = {
    ".py": [r"#.*", r'"""[\s\S]*?"""', r"'''[\s\S]*?'''"],
    ".c": [r"//.*", r"/\*[\s\S]*?\*/"],
    ".cpp": [r"//.*", r"/\*[\s\S]*?\*/"],
    ".java": [r"//.*", r"/\*[\s\S]*?\*/"],
    ".js": [r"//.*", r"/\*[\s\S]*?\*/"],
    ".ts": [r"//.*", r"/\*[\s\S]*?\*/"],
    ".sh": [r"#.*"],
    ".rb": [r"#.*"],
    ".go": [r"//.*", r"/\*[\s\S]*?\*/"],
    ".php": [r"//.*", r"/\*[\s\S]*?\*/", r"#.*"],
    ".html": [r"<!--[\s\S]*?-->"],
    ".css": [r"/\*[\s\S]*?\*/"],
}

def remove_comments_from_text(text, ext):
    patterns = COMMENT_PATTERNS.get(ext.lower(), [])
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.MULTILINE)
    return text

def backup_file(file_path):
    try:
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        return backup_path
    except Exception as e:
        print(f"Failed to backup {file_path}: {e}")
        return None

def is_text_file(filepath, blocksize=512):
    try:
        with open(filepath, 'rb') as f:
            block = f.read(blocksize)
        if b'\0' in block:
            return False
        return True
    except Exception:
        return False

def process_file(file_path):
    if not is_text_file(file_path):
        return
    ext = os.path.splitext(file_path)[1]
    if ext.lower() not in COMMENT_PATTERNS:
        return  # Skip unknown file types
    try:
        backup_file(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = remove_comments_from_text(content, ext)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Processed: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_directory(directory):
    for root, _, files in os.walk(directory):
        if '.git' in root.split(os.sep):
            continue  # skip git internals
        for file in files:
            process_file(os.path.join(root, file))

def check_write_access(repo_dir):
    try:
        result = subprocess.run(
            ["git", "-C", repo_dir, "push", "--dry-run"],
            capture_output=True, text=True
        )
        if "Permission denied" in result.stderr or "fatal" in result.stderr:
            return False
        return True
    except Exception:
        return False

def process_git_repo(repo_url, files_to_process=None):
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
        if files_to_process:
            for f in files_to_process:
                full_path = os.path.join(temp_dir, f)
                if os.path.exists(full_path):
                    process_file(full_path)
                else:
                    print(f"File not found in repo: {f}")
        else:
            process_directory(temp_dir)

        subprocess.run(["git", "-C", temp_dir, "add", "."], check=True)
        result = subprocess.run(["git", "-C", temp_dir, "status", "--porcelain"], capture_output=True, text=True)
        if not result.stdout.strip():
            print("No changes detected in git repo; nothing to commit.")
            return

        subprocess.run(["git", "-C", temp_dir, "commit", "-m", "Removed comments"], check=True)

        if not check_write_access(temp_dir):
            if repo_url.startswith("https://"):
                print("No write access detected. Provide a GitHub Personal Access Token (PAT) to push changes.")
                pat = getpass.getpass("Enter your PAT: ")
                split_url = repo_url.replace("https://", "").split("/", 1)
                token_url = f"https://{pat}@{split_url[0]}/{split_url[1]}"
                subprocess.run(["git", "-C", temp_dir, "push", token_url, "HEAD"], check=True)
            elif repo_url.startswith("git@") or repo_url.startswith("ssh://"):
                print("No write access detected for SSH. Make sure your SSH key has permission to push.")
            else:
                print("Unknown repo URL format. Skipping push.")
        else:
            subprocess.run(["git", "-C", temp_dir, "push"], check=True)

        print("Git repo processed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")
    finally:
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove comments from code files safely")
    parser.add_argument("-f", "--file", help="File to process")
    parser.add_argument("-d", "--dir", help="Directory to process recursively")
    parser.add_argument("-g", "--git", help="Git repository URL to process")
    parser.add_argument("--git-files", nargs='+', help="Specific files in git repo to process")
    args = parser.parse_args()

    if args.file:
        if os.path.isfile(args.file):
            process_file(args.file)
        else:
            print(f"File does not exist: {args.file}")
    elif args.dir:
        if os.path.isdir(args.dir):
            process_directory(args.dir)
        else:
            print(f"Directory does not exist: {args.dir}")
    elif args.git:
        process_git_repo(args.git, files_to_process=args.git_files)
    else:
        print("Please provide --file, --dir, or --git argument.")