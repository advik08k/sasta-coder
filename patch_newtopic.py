import os, re

repo_dir = 'C:/Users/abcd/.gemini/antigravity/scratch/sasta-coder-repo'
main_file = os.path.join(repo_dir, 'render_main.py')

with open(main_file, 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add /newtopic command
newtopic_code = '''
    async def cmd_newtopic(u: Update, c):
        if not auth(u): return
        mem = get_mem(MY_USER_ID)
        if "archive" not in mem: mem["archive"] = []
        mem["archive"].extend(mem.get("history", []))
        mem["history"] = []
        save_mem(MY_USER_ID)
        await u.message.reply_text("?? Naya topic shuru! Purani baatein archive mein safe hain aur context reset ho gaya hai.", reply_markup=main_keyboard())
'''

# Find cmd_clear and insert cmd_newtopic after it
c = c.replace("async def cmd_clear(u: Update, c):", newtopic_code.strip() + "\n\n    async def cmd_clear(u: Update, c):")

# Register handler for /newtopic
handler_code = '''app.add_handler(CommandHandler("newtopic", cmd_newtopic))'''
c = c.replace('app.add_handler(CommandHandler("clear", cmd_clear))', 'app.add_handler(CommandHandler("clear", cmd_clear))\n    ' + handler_code)

# 2. Add sliding window memory
# Locate: hist_copy = list(mem["history"])
sliding_window_old = '''hist_copy = list(mem["history"])'''
sliding_window_new = '''# SLIDING WINDOW: Only keep the last 20 messages for context
            hist_copy = list(mem["history"])[-20:]'''
c = c.replace(sliding_window_old, sliding_window_new)

with open(main_file, 'w', encoding='utf-8') as f:
    f.write(c)

print("Sliding window and /newtopic implemented successfully!")
