with open("render_main.py", "r", encoding="utf-8") as f:
    c = f.read()

# The broken parts look like:
# await status_msg.edit_text(f"`\text\n{result[:3500]}\n`", parse_mode=ParseMode.MARKDOWN)
# Or similar, due to powershell string interpolation.
import re
c = re.sub(r'await status_msg\.edit_text\(f"`\s*ext\n(.*?)`", parse_mode=ParseMode\.MARKDOWN\)', r'await status_msg.edit_text(f"```text\\n\1```", parse_mode=ParseMode.MARKDOWN)', c, flags=re.DOTALL)

with open("render_main.py", "w", encoding="utf-8") as f:
    f.write(c)
