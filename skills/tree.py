import os, sys
path = sys.argv[1] if len(sys.argv) > 1 else "."
for root, dirs, files in os.walk(path):
    if '.git' in root or '__pycache__' in root or '.venv' in root: continue
    level = root.replace(path, '').count(os.sep)
    indent = ' ' * 4 * (level)
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 4 * (level + 1)
    for f in files: print(f"{subindent}{f}")
