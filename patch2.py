import re

with open('C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo/render_main.py', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Update System Prompt
old_sp_part = '''5. GENERAL INSTRUCTIONS:'''
new_sp_part = '''7. TERMINAL ACCESS (Render Sandbox):
To run bash/shell commands on the host server (Linux), use:
`ash
# RUN_TERMINAL
ls -la
`
8. WEB SCRAPING:
To fetch the raw text content of a website, use:
`
# FETCH_URL
https://example.com
`

9. GENERAL INSTRUCTIONS:
- IMPORTANT: You are provided with the full chat history. DO NOT re-answer old questions. ONLY respond to the LATEST user message at the very end of the history.
'''
c = c.replace(old_sp_part, new_sp_part)

# 2. Add regex matching for new tools
old_regex = '''code_match = re.search(r'`python\s*# EXECUTE\s*(.*?)`', reply, re.DOTALL)'''
new_regex = '''code_match = re.search(r'`python\s*# EXECUTE\s*(.*?)`', reply, re.DOTALL)
            term_match = re.search(r'`(?:bash|sh)?\s*# RUN_TERMINAL\s*(.*?)`', reply, re.DOTALL)
            url_match = re.search(r'`\s*# FETCH_URL\s*(.*?)`', reply, re.DOTALL)'''
c = c.replace(old_regex, new_regex)

# 3. Add execution logic for new tools
old_exec = '''            if api_match:'''
new_exec = '''            if term_match:
                cmd = term_match.group(1).strip()
                status_msg = await u.message.reply_text(f"??? Running: {cmd}...", parse_mode=ParseMode.MARKDOWN)
                try:
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=30).decode('utf-8', errors='replace')
                except subprocess.CalledProcessError as e:
                    result = e.output.decode('utf-8', errors='replace')
                except Exception as e:
                    result = str(e)
                if not result.strip(): result = "(Success with no output)"
                await status_msg.edit_text(f"`	ext\n{result[:3500]}\n`", parse_mode=ParseMode.MARKDOWN)
                h.append({"role": "user", "content": f"Terminal Result:\n{result}\nAnalyze this and answer the user."})
                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            elif url_match:
                url = url_match.group(1).strip()
                status_msg = await u.message.reply_text(f"?? Fetching: {url}...", parse_mode=ParseMode.MARKDOWN)
                try:
                    r = requests.get(url, timeout=15)
                    result = r.text[:10000] # get first 10k chars
                except Exception as e:
                    result = str(e)
                await status_msg.edit_text(f"`	ext\n(Fetched {len(result)} bytes)\n`", parse_mode=ParseMode.MARKDOWN)
                h.append({"role": "user", "content": f"Website Content:\n{result}\nAnalyze this and answer the user."})
                await c.bot.send_chat_action(chat_id=u.effective_chat.id, action="typing")
                current_turn += 1
                continue
            elif api_match:'''
c = c.replace(old_exec, new_exec)

# 4. Fix memory flattening by adding a strict instruction to the very last user message
old_mem = '''msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + mem["history"]'''
new_mem = '''
            # Prevent Claude from answering all history at once
            hist_copy = list(mem["history"])
            if hist_copy and hist_copy[-1]["role"] == "user":
                hist_copy[-1] = {"role": "user", "content": hist_copy[-1]["content"] + "\\n\\n[SYSTEM NOTE: This is the latest message. DO NOT reply to previous history, only reply to this specific prompt.]"}
            msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + hist_copy
'''
c = c.replace(old_mem, new_mem)

with open('C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo/render_main.py', 'w', encoding='utf-8') as f:
    f.write(c)
print("Added Terminal, Web Scraper, and Memory fix!")
