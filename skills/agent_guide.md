# Agent Architecture Guide
When the user asks for help building AI Agents, follow these Antigravity principles:
1. **Tool Use (Hands & Legs)**: An agent is just an LLM in a while loop that outputs specially formatted tags (like # RUN_TERMINAL) which a host script parses, executes, and feeds the result back into the chat history.
2. **Memory Management**: Keep chat history clean. Summarize old turns if the context window gets too large. 
3. **State Machines**: Advanced agents use DAGs (Directed Acyclic Graphs) or State Machines (like LangGraph) instead of pure loops to ensure reliability.
4. **Error Correction**: When a tool fails (e.g. traceback), the host script MUST feed the exact error string back to the LLM so it can self-correct.
