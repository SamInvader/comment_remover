#!/usr/bin/env python3
import os
import re
import tempfile
import shutil
import subprocess
import argparse

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

def backup_file(file_path, dest_folder=None):
    try:
        if dest_folder:
            os.makedirs(dest_folder, exist_ok=True)
            backup_path = os.path.join(dest_folder, os.path.basename(file_path))
        else:
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
        return b'\0' not in block
    except Exception:
        return False

def process_file(file_path, dest_folder=None):
    if not is_text_file(file_path):
        return
    ext = os.path.splitext(file_path)[1]
    if ext.lower() not in COMMENT_PATTERNS:
        return  # Skip unknown file types
    try:
        backup_file(file_path, dest_folder=dest_folder)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = remove_comments_from_text(content, ext)
        output_path = os.path.join(dest_folder, os.path.basename(file_path)) if dest_folder else file_path
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Processed: {file_path} -> {output_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_directory(directory, dest_folder=None):
    for root, _, files in os.walk(directory):
        if '.git' in root.split(os.sep):
            continue  # skip git internals
        for file in files:
            process_file(os.path.join(root, file), dest_folder=dest_folder)

def process_git_repo(repo_url, files_to_process=None, output_folder="processed_repo"):
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
        dest_dir = os.path.join(os.getcwd(), output_folder)
        if files_to_process:
            for f in files_to_process:
                full_path = os.path.join(temp_dir, f)
                if os.path.exists(full_path):
                    process_file(full_path, dest_folder=dest_dir)
                else:
                    print(f"File not found in repo: {f}")
        else:
            process_directory(temp_dir, dest_folder=dest_dir)
        print(f"Processed repo saved to folder: {dest_dir}")
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
    parser.add_argument("--output", help="Folder to save processed files", default="processed_files")
    args = parser.parse_args()

    if args.file:
        if os.path.isfile(args.file):
            process_file(args.file, dest_folder=args.output)
        else:
            print(f"File does not exist: {args.file}")
    elif args.dir:
        if os.path.isdir(args.dir):
            process_directory(args.dir, dest_folder=args.output)
        else:
            print(f"Directory does not exist: {args.dir}")
    elif args.git:
        process_git_repo(args.git, files_to_process=args.git_files, output_folder=args.output)
    else:
        print("Please provide --file, --dir, or --git argument.")