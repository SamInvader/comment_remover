# Dynamic Comment Remover

A Python script that safely removes comments from code files, directories, or Git repositories. It supports multiple languages and automatically detects file types. Git integration allows pushing changes via SSH or HTTPS with a Personal Access Token (PAT).

---

## Features

- Dynamic Language Detection: Automatically detects the programming language by file extension.  
- Generic Fallback: Removes comments in unknown file types using common comment patterns (#, //, /* */, <!-- -->).  
- Backups: Creates .bak files before modifying.  
- Directory Support: Process entire directories recursively.  
- Git Repository Support:  
  - Clones, modifies, commits, and pushes changes automatically.  
  - Supports SSH authentication.  
  - HTTPS authentication via PAT if write access is needed.  
  - Only pushes if write access exists.  
- Safe: Only modifies files in-place, errors are handled gracefully.  

---

## Supported File Types

Python (.py), C/C++ (.c, .cpp), Java (.java), JavaScript (.js, .ts), Shell (.sh), Ruby (.rb), Go (.go), PHP (.php), HTML (.html), CSS (.css)  
Unknown file extensions fall back to generic comment patterns.

---

## Installation

```bash
git clone https://github.com/yourusername/dynamic-comment-remover.git
cd dynamic-comment-remover
python remove_comments.py --help
```

---

## Usage

- Single File

python remove_comments.py --file path/to/file.py

- Directory

 python remove_comments.py --dir path/to/directory

- Git Repository

python remove_comments.py --git https://github.com/user/repo.git

  - SSH URL Example: git@github.com:user/repo.git

  - HTTPS URL: You may be prompted for a Personal Access Token (PAT) if push access is required.



---

## Safety Notes

A backup of each modified file is created with a .bak extension.

Only attempts to push if write access exists; otherwise, it prompts for PAT (HTTPS) or warns (SSH).



---

## License

MIT License



