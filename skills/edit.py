import sys, os
if len(sys.argv) < 3:
    print("Usage: python edit.py <file_path> <mode> <content>")
    print("Modes: 'write' (overwrite), 'append' (add to end)")
    sys.exit(1)

file_path = sys.argv[1]
mode = sys.argv[2]
content = sys.stdin.read() if not sys.stdin.isatty() else "\n".join(sys.argv[3:])

try:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w' if mode == 'write' else 'a', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully {mode}d to {file_path}")
except Exception as e:
    print(f"Error: {e}")
