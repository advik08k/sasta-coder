import os

repo_dir = 'C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo'
skills_dir = os.path.join(repo_dir, 'skills')

# 1. File Editor Skill (Crucial for coding agents)
edit_code = '''import sys, os
if len(sys.argv) < 3:
    print("Usage: python edit.py <file_path> <mode> <content>")
    print("Modes: 'write' (overwrite), 'append' (add to end)")
    sys.exit(1)

file_path = sys.argv[1]
mode = sys.argv[2]
content = sys.stdin.read() if not sys.stdin.isatty() else "\\n".join(sys.argv[3:])

try:
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w' if mode == 'write' else 'a', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully {mode}d to {file_path}")
except Exception as e:
    print(f"Error: {e}")
'''
with open(os.path.join(skills_dir, 'edit.py'), 'w', encoding='utf-8') as f: f.write(edit_code)

# 2. Directory Tree Skill (To explore codebases)
tree_code = '''import os, sys
path = sys.argv[1] if len(sys.argv) > 1 else "."
for root, dirs, files in os.walk(path):
    if '.git' in root or '__pycache__' in root or '.venv' in root: continue
    level = root.replace(path, '').count(os.sep)
    indent = ' ' * 4 * (level)
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 4 * (level + 1)
    for f in files: print(f"{subindent}{f}")
'''
with open(os.path.join(skills_dir, 'tree.py'), 'w', encoding='utf-8') as f: f.write(tree_code)

# 3. Agent Architect Guide (Knowledge Base)
agent_guide = '''# Agent Architecture Guide
When the user asks for help building AI Agents, follow these Antigravity principles:
1. **Tool Use (Hands & Legs)**: An agent is just an LLM in a while loop that outputs specially formatted tags (like # RUN_TERMINAL) which a host script parses, executes, and feeds the result back into the chat history.
2. **Memory Management**: Keep chat history clean. Summarize old turns if the context window gets too large. 
3. **State Machines**: Advanced agents use DAGs (Directed Acyclic Graphs) or State Machines (like LangGraph) instead of pure loops to ensure reliability.
4. **Error Correction**: When a tool fails (e.g. traceback), the host script MUST feed the exact error string back to the LLM so it can self-correct.
'''
with open(os.path.join(skills_dir, 'agent_guide.md'), 'w', encoding='utf-8') as f: f.write(agent_guide)

# Update SYSTEM_PROMPT in render_main.py
with open(os.path.join(repo_dir, 'render_main.py'), 'r', encoding='utf-8') as f:
    c = f.read()

dev_skills_part = '''
10. DEVELOPER & AGENT SKILLS:
You are an expert at helping the user BUILD AGENTS and WRITE CODE. Use these tools via # RUN_TERMINAL:
- python skills/tree.py . (Explore codebase directory structure)
- python skills/edit.py <filepath> write "<content>" (Create or overwrite a file. NOTE: Better to use cat << 'EOF' > file for complex code)
- cat skills/agent_guide.md (Read agent building best practices)

To edit or create files with complex code, ALWAYS use bash heredocs via # RUN_TERMINAL:
`ash
# RUN_TERMINAL
cat << 'EOF' > my_script.py
import os
print("Hello Agent")
EOF
`
This is the most reliable way to write code on the host server.
'''

import re
# Replace the old PRE-BUILT SKILLS block
c = re.sub(r'10\. PRE-BUILT SKILLS.*?11\. AGENTIC SUPERPOWERS:.*?(?=\n9\. GENERAL INSTRUCTIONS:)', dev_skills_part, c, flags=re.DOTALL)

with open(os.path.join(repo_dir, 'render_main.py'), 'w', encoding='utf-8') as f:
    f.write(c)

print("Developer skills and Agent Architect context added!")
