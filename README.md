# Safe Comment Remover

A Python script to safely remove comments from code files.  

- **Python files** are processed using **AST**, preserving docstrings and essential metadata.  
- **Other languages** (C, C++, Java, JS, TS, HTML, CSS, etc.) use regex for comment removal. ⚠️ Note: Regex removal may break code if comments are critical.  
- All files are **backed up** before modification.  
- Processed files are saved in a separate folder; your originals remain untouched.  

## Features

- Safe Python comment removal (docstrings preserved)  
- Supports multiple languages with regex removal  
- Process single files, directories, or Git repositories  
- Automatic backup before modification  
- Output saved in a dedicated folder  

## Usage

```bash
# Process a single file
python remove.py -f script.py --output processed

# Process a directory recursively
python remove.py -d my_project/ --output processed

# Process a Git repository
python remove.py -g https://github.com/user/repo.git --output processed_repo

# Process specific files in a Git repository
python remove.py -g https://github.com/user/repo.git --git-files src/main.py src/utils.py --output processed_repo
```

# Important:

- Python comments are safely removed without breaking docstrings.

- For non-Python languages, removing comments via regex can sometimes break the system if the comments are essential.

- Always check your output folder before replacing the original files.
