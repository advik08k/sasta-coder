import re

with open('C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo/render_main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix the broken backticks caused by powershell
c = c.replace('`\text\n', '```text\\n')
c = c.replace('`\t', '```t')
c = c.replace('`", parse_mode', '```", parse_mode')

# Actually, let's just use regex to fix the edit_text calls in term_match and url_match
c = re.sub(r'await status_msg\.edit_text\(f"`\s*ext\n(.*?)\n`", parse_mode=ParseMode\.MARKDOWN\)', 
           r'await status_msg.edit_text(f"```text\\n\1\\n```", parse_mode=ParseMode.MARKDOWN)', c)

with open('C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo/render_main.py', 'w', encoding='utf-8') as f:
    f.write(c)
