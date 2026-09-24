with open("render_main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if 'await status_msg.edit_text(f"```text' in line:
        # replace this line and the next line with a single line
        # f"```text\n{result[:3500]}\n```"
        if i+1 < len(lines) and '```"' in lines[i+1]:
            var_name = '{result[:3500]}' if '{result[:3500]}' in line else '{len(result)}'
            new_lines.append(f'                await status_msg.edit_text(f"```text\\n{var_name}\\n```", parse_mode=ParseMode.MARKDOWN)\n')
            i += 2
            continue
    if 'h.append({"role": "user", "content": f"Terminal Result:' in line:
        new_lines.append('                h.append({"role": "user", "content": f"Terminal Result:\\n{result}\\nAnalyze this and answer the user."})\n')
        i += 3
        continue
    if 'h.append({"role": "user", "content": f"Website Content:' in line:
        new_lines.append('                h.append({"role": "user", "content": f"Website Content:\\n{result}\\nAnalyze this and answer the user."})\n')
        i += 3
        continue
    new_lines.append(line)
    i += 1

with open("render_main.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)
