"""Generate notebooks/01_agent_loop.ipynb"""
#  this file is designed just to validate the work for LLMs, you can ignore that

import json
import os

NB_VERSION = 4
NB_MINOR = 5

KERNEL_SPEC = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}

LANG_INFO = {
    "name": "python",
    "version": "3.10.0",
}


CELL_META = {}

def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": CELL_META,
        "source": [source],
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": CELL_META,
        "outputs": [],
        "source": [source],
    }


PROVIDER_CONFIG_TABLE = r'''import os
from pathlib import Path
from openai import OpenAI
import getpass

# --- Optional .env file loading (no extra pip installs needed) ---
env_path = Path.cwd() / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    print("Loaded .env file.")
else:
    print("No .env file found — you will be prompted for API keys.")
    print("  Tip: cp .env.example .env  and fill in your keys to skip prompts.")

PROVIDER = "groq"  # Choose: groq, openrouter

MOCK = {
    "groq":       True,
    "openrouter": True,
}

# Environment variable names for auto-loading keys (set in .env)
KEY_ENV_VAR = {
    "groq":       "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

CONFIG = {
    "groq": {
        "name": "Groq",
        "model": "openai/gpt-oss-20b",
        "key_url": "https://console.groq.com/keys",
        "base_url": "https://api.groq.com/openai/v1",
    },
    "openrouter": {
        "name": "OpenRouter",
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "key_url": "https://openrouter.ai/keys",
        "base_url": "https://openrouter.ai/api/v1",
    },
}

cfg = CONFIG[PROVIDER]
use_mock = MOCK[PROVIDER]

if use_mock:
    print(f"[{cfg['name']}] Mock mode enabled.")
    client = None
else:
    api_key = os.environ.get(KEY_ENV_VAR[PROVIDER]) or getpass.getpass(f"Enter your {cfg['name']} API key: ")
    client = OpenAI(api_key=api_key, base_url=cfg["base_url"])
    print(f"[{cfg['name']}] API key configured.")
'''

# Shared mock LLM that can trigger tool calls
MOCK_AGENT_MODEL = r'''
def mock_agent_model(messages):
    """Mock LLM for agent demo. Returns tool-call-like responses."""
    last = messages[-1]["content"] if messages else ""
    lower = last.lower()

    if "calc" in lower or "math" in lower or "+" in last or "-" in last or "*" in last or "/" in last:
        return 'TOOL: calculator, args: {"expr": "' + last.replace('"', "'") + '"}'
    if "weather" in lower:
        return 'TOOL: get_weather, args: {"city": "' + last.replace("weather in ", "").replace("?","").strip() + '"}'
    if "read" in lower or "file" in lower:
        return 'TOOL: read_file, args: {"path": "notes.txt"}'
    if last:
        return f'I processed your request: "{last[:50]}"'
    return "I am a mock agent. I process requests step by step."
'''

ALL_CELLS = [
    # ---- Title ----
    md(
        '# Notebook 01: The Agent Loop\n'
        '\n'
        'We move from single-turn LLM calls to agents that plan, act, observe, and adapt.\n'
        '\n'
        '**Expected time:** ~45 minutes\n'
        '**Prerequisites:** Notebook 00\n'
    ),

    # ---- What you'll learn ----
    md(
        '## What You\'ll Learn\n'
        '\n'
        '1. The difference between a chatbot and an agent\n'
        '2. The ReAct pattern: Thought → Action → Observation → repeat\n'
        '3. Use a pre-built agent from the helper module\n'
        '4. Define tools and connect them to an agent\n'
        '5. Recognize and fix common agent failures\n'
        '6. Peek under the hood at a simplified loop implementation\n'
    ),

    # ---- Setup ----
    md(
        '## Setup\n'
        '\n'
        'Run the cell below to install packages and import helpers. '
        'If you skipped Notebook 00, you\'ll also need an API key (see Notebook 00 for instructions).\n'
        '\n'
        'This notebook supports **Groq** and **OpenRouter**. '
        'The default OpenRouter model is `nvidia/nemotron-3-ultra-550b-a55b:free`. '
        'Set your provider\'s mock flag to `True` if you have no API key.'
    ),
    code(
        '!pip install openai==1.68.2 groq==0.18.0\n'
        '\n'
        'from agent_helpers import ReactAgent, make_tool, mock_llm, mock_search, tools_to_openai_native\n'
        'import getpass\n'
        'import inspect\n'
        'import json\n'
        '\n'
        + PROVIDER_CONFIG_TABLE
    ),

    # ---- Model wrapper ----
    md(
        '### Model Wrapper\n'
        '\n'
        'The agent loop needs a function that sends messages to the LLM and returns the response text. '
        'This wrapper adapts the provider SDK to the simple interface `ReactAgent` expects.'
    ),
    code(
        'def make_model(client, model_name=None, system_prompt_tools=None):\n'
        '    """Wrap provider client as a callable for ReactAgent.\n'
        '\n'
        '    Uses native function calling API (tools param) for robust tool use.\n'
        '    """\n'
        '    if model_name is None:\n'
        '        model_name = cfg["model"]\n'
        '\n'
        '    native_tools = None\n'
        '    system_prompt = None\n'
        '\n'
        '    if system_prompt_tools:\n'
        '        native_tools = tools_to_openai_native(system_prompt_tools)\n'
        '        system_prompt = (\n'
        '            "You have access to tools. Use them when needed to answer user questions."\n'
        '            " If you can answer without a tool, respond directly."\n'
        '        )\n'
        '\n'
        '    def model_fn(messages):\n'
        '        msgs = messages\n'
        '        if system_prompt and not any(m.get("role") == "system" for m in msgs):\n'
        '            msgs = [{"role": "system", "content": system_prompt}] + msgs\n'
        '\n'
        '        kwargs = {"model": model_name, "messages": msgs}\n'
        '        if native_tools:\n'
        '            kwargs["tools"] = native_tools\n'
        '\n'
        '        response = client.chat.completions.create(**kwargs)\n'
        '        msg = response.choices[0].message\n'
        '\n'
        '        if msg.tool_calls:\n'
        '            tc = msg.tool_calls[0]\n'
        '            return {\n'
        '                "type": "tool_call",\n'
        '                "name": tc.function.name,\n'
        '                "args": json.loads(tc.function.arguments),\n'
        '                "tool_call_id": tc.id,\n'
        '            }\n'
        '        return {"type": "text", "content": msg.content}\n'
        '\n'
        '    return model_fn\n'
    ),

    # ---- Chatbot vs Agent ----
    md(
        '## Chatbot vs. Agent\n'
        '\n'
        'A **chatbot** answers once. An **agent** loops: it can call tools, see results, and decide what to do next.\n'
        '\n'
        'Let\'s see the difference side by side with the same task:\n'
        '> *"What is (15 * 3) + 42 / 2?"*\n'
    ),

    # Chatbot version
    md('### Chatbot (Single Turn)\n'),
    code(
        'if not use_mock and client is not None:\n'
        '    model = make_model(client, cfg["model"])\n'
        '    reply = model([{"role": "user", "content": "What is (15 * 3) + 42 / 2?"}])\n'
        '    print("Chatbot response:")\n'
        '    print(reply)\n'
        '    print("\\nOne answer. No follow-up. No tool use.")\n'
        'else:\n'
        '    print("Mock — chatbot would respond with the computed answer.")\n'
        '    print("But a real LLM might calculate wrong without a tool.")\n'
    ),

    # ---- Agent version ----
    md(
        '### Agent (With Tool)\n'
    ),
    code(
        '# Define a calculator tool\n'
        'def calculator(expr):\n'
        '    try:\n'
        '        return str(eval(expr))\n'
        '    except Exception as e:\n'
        '        return f"Error: {e}"\n'
        '\n'
        'tools = [make_tool("calculator", "Evaluate arithmetic expressions", calculator)]\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    model = make_model(client, cfg["model"], system_prompt_tools=tools)\n'
        '    agent = ReactAgent(model=model, tools=tools)\n'
        '    result = agent.run("What is (15 * 3) + 42 / 2?")\n'
        '    print("Agent response:")\n'
        '    print(result)\n'
        '    print("\\nThe agent called the calculator tool internally to get the exact answer.")\n'
        'else:\n'
        '    mock_model = mock_llm("TOOL: calculator, args: {\\"expr\\": \\"(15*3)+(42/2)\\"}")\n'
        '    agent = ReactAgent(model=mock_model, tools=tools)\n'
        '    result = agent.run("What is (15 * 3) + 42 / 2?")\n'
        '    print("Agent response (mock):")\n'
        '    print(result)\n'
    ),

    # ---- Tool definition pattern ----
    md(
        '## Tool Definition Pattern\n'
        '\n'
        'Tools are the agent\'s hands. Each tool has a name, description, and function.\n'
        '\n'
        '```python\n'
        'tools = [\n'
        '    make_tool("name", "what it does", function),\n'
        '    make_tool("another", "description", another_function),\n'
        ']\n'
        '```\n'
        '\n'
        'Let\'s build a multi-tool agent that decides *which* tool to call based on the question.'
    ),
    code(
        'def calculator(expr):\n'
        '    try:\n'
        '        return f"Result: {eval(expr)}"\n'
        '    except Exception as e:\n'
        '        return f"Calculation error: {e}"\n'
        '\n'
        'def get_weather(city):\n'
        '    """Mock weather lookup."""\n'
        '    data = {\n'
        '        "Chisinau": "18°C, partly cloudy",\n'
        '        "Copenhagen": "12°C, light rain",\n'
        '        "Athens": "28°C, sunny",\n'
        '        "Vienna": "15°C, overcast",\n'
        '    }\n'
        '    return data.get(city, f"Weather data not available for {city}")\n'
        '\n'
        'def read_file(path):\n'
        '    """Mock file reader."""\n'
        '    files = {\n'
        '        "notes.txt": "Agentic AI systems use a loop: plan, act, observe, adapt.",\n'
        '        "todo.txt": "1. Finish agent loop notebook\\n2. Start PBL project",\n'
        '    }\n'
        '    return files.get(path, f"File not found: {path}")\n'
        '\n'
        'tools = [\n'
        '    make_tool("calculator", "Evaluate math expressions", calculator),\n'
        '    make_tool("get_weather", "Get weather for a city", get_weather),\n'
        '    make_tool("read_file", "Read contents of a file", read_file),\n'
        ']\n'
        '\n'
        'print("Tools defined:")\n'
        'for t in tools:\n'
        '    print(f"  - {t[\'name\']}: {t[\'description\']}")\n'
    ),

    # ---- Run multi-tool ----
    md(
        '### Multi-Tool Agent in Action\n'
        '\n'
        'Give the agent different questions and watch it pick the right tool.'
    ),
    code(
        'if not use_mock and client is not None:\n'
        '    model = make_model(client, cfg["model"], system_prompt_tools=tools)\n'
        '    agent = ReactAgent(model=model, tools=tools)\n'
        '\n'
        '    questions = [\n'
        '        "What is 2 + 2?",\n'
        '        "What is the weather in Chisinau?",\n'
        '        "Read my notes.txt file",\n'
        '    ]\n'
        '\n'
        '    for q in questions:\n'
        '        print(f">>> {q}")\n'
        '        print(agent.run(q))\n'
        '        print()\n'
        'else:\n'
        '    print("Mock mode — multi-tool agent responses would look like:")\n'
        '    print(\'  >>> What is 2 + 2?\'); print("  4")\n'
        '    print(\'  >>> What is the weather in Chisinau?\'); print("  18°C, partly cloudy")\n'
        '    print(\'  >>> Read my notes.txt\'); print("  Agentic AI systems use a loop: plan, act, observe, adapt.")\n'
    ),

    # ---- Peek under hood ----
    md(
        '## Peek Under the Hood\n'
        '\n'
        'Here\'s a simplified version of how `ReactAgent` works internally. '
        'You don\'t need to write this — the helper module handles it — but reading it helps you understand the loop.'
    ),
    code(
        'class SimpleReactAgent:\n'
        '    """Simplified agent loop (15 lines). Read, don\'t type."""\n'
        '    def __init__(self, model, tools, max_steps=5):\n'
        '        self.model = model\n'
        '        self.tools = {t["name"]: t for t in tools}\n'
        '        self.history = []\n'
        '        self.max_steps = max_steps\n'
        '\n'
        '    def run(self, user_input):\n'
        '        for step in range(self.max_steps):\n'
        '            response = self.model(self.history + [{"role": "user", "content": user_input}])\n'
        '            if "TOOL:" in response:\n'
        '                name, args = self._parse(response)\n'
        '                result = self.tools[name]["fn"](**args)\n'
        '                self.history.append({"role": "tool", "content": str(result)})\n'
        '            else:\n'
        '                return response\n'
        '        return "Max steps reached"\n'
        '\n'
        '    def _parse(self, response):\n'
        '        parts = response.replace("TOOL:", "").strip().split(", args:")\n'
        '        name = parts[0].strip()\n'
        '        args = json.loads(parts[1]) if len(parts) > 1 else {}\n'
        '        return name, args\n'
        '\n'
        'print("Simplified agent loop — 15 lines.")\n'
        'print("The full version in agent_helpers.py adds error handling and better parsing.")\n'
    ),

    # ---- What breaks ----
    md(
        '## What Breaks?\n'
        '\n'
        'Agents fail in predictable ways. Let\'s break things on purpose.\n'
    ),

    md(
        '### Break 1: Infinite Loop\n'
        '\n'
        'Without a `max_steps` limit, an agent that never produces a final answer runs forever.'
    ),
    code(
        'def stuck_model(messages):\n'
        '    """Model that never gives a final answer — always calls a tool."""\n'
        '    return "TOOL: calculator, args: {\\"expr\\": \\"1+1\\"}"\n'
        '\n'
        'stuck_agent = ReactAgent(\n'
        '    model=stuck_model,\n'
        '    tools=[make_tool("calculator", "calc", lambda x: "2")],\n'
        '    max_steps=3,  # Low limit so we see the stop quickly\n'
        ')\n'
        'result = stuck_agent.run("keep going")\n'
        'print("Result after hitting max_steps=3:")\n'
        'print(result)\n'
        'print("\\n☝️ The max_steps parameter is the safety net. Always set it.")\n'
    ),

    md(
        '### Break 2: Bad Tool JSON\n'
        '\n'
        'The LLM sometimes generates malformed tool calls. The agent needs to handle this gracefully.'
    ),
    code(
        'def bad_json_model(messages):\n'
        '    """Model that returns unparseable JSON arguments."""\n'
        '    return "TOOL: calculator, args: {invalid json here}"\n'
        '\n'
        'try:\n'
        '    agent = ReactAgent(\n'
        '        model=bad_json_model,\n'
        '        tools=[make_tool("calculator", "calc", lambda x: "2")],\n'
        '    )\n'
        '    agent.run("crash me")\n'
        'except json.JSONDecodeError as e:\n'
        '    print(f"Error: Malformed JSON from model — {e}")\n'
        '    print("\\nFix: Wrap json.loads() in try/except. In agent_helpers.py, this is already handled.")\n'
    ),

    md(
        '### Break 3: Tool Not Found\n'
        '\n'
        'The LLM requests a tool that doesn\'t exist. The agent needs to tell the LLM what\'s available.'
    ),
    code(
        'def wrong_tool_model(messages):\n'
        '    return "TOOL: send_email, args: {}"\n'
        '\n'
        'agent = ReactAgent(\n'
        '    model=wrong_tool_model,\n'
        '    tools=[make_tool("calculator", "calc", lambda x: "2")],\n'
        ')\n'
        'result = agent.run("do something")\n'
        'print("Agent response:")\n'
        'print(result)\n'
        'print("\\nThe agent included the available tools in the error message. The LLM can try again with a valid tool.")\n'
    ),

    # ---- Connection to Agentic AI ----
    md(
        '## Connection to Agentic AI\n'
        '\n'
        'The loop is what makes AI *agentic*. Without it, you have a chatbot — a one-shot answer generator. '
        'With it, the system can pursue multi-step goals, recover from failures, and use the real world (via tools).\n'
        '\n'
        'This maps directly to **Complexity Ladder Level 1-2**:\n'
        '- **Level 1:** One LLM call + one external tool (you did this with the calculator)\n'
        '- **Level 2:** A loop with max_steps (you did this with the ReactAgent)\n'
        '\n'
        'Every project in this course will be built on this loop.'
    ),

    # ---- PBL reflection ----
    md(
        '### PBL Reflection\n'
    ),
    code(
        'print("Think about your PBL project:")\n'
        'print("  1. What task could your project automate with a loop?")\n'
        'print("  2. What tools would your agent need?")\n'
        'print("  3. Where might the loop get stuck? How would you protect it?")\n'
        'print("\\nWrite your thoughts in your project journal.")\n'
    ),

    # ---- Exercises ----
    md(
        '## Exercises\n'
    ),

    md(
        '### Bronze — Run and Observe\n'
        '\n'
        'Run the cell below. It creates an agent with a custom tool and runs 3 different prompts. '
        'Change the prompts and observe how the agent responds.'
    ),
    code(
        'def search_web(query):\n'
        '    """Mock web search."""\n'
        '    results = {\n'
        '        "agentic ai": "Agentic AI refers to systems that can pursue goals autonomously.",\n'
        '        "python": "Python is a programming language widely used for AI and data science.",\n'
        '        "PBL": "Problem-Based Learning: students learn by solving open-ended problems.",\n'
        '    }\n'
        '    return results.get(query.lower(), f"Search results for: {query}")\n'
        '\n'
        'search_tools = [make_tool("search", "Search the web", search_web)]\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    model = make_model(client, cfg["model"], system_prompt_tools=search_tools)\n'
        '    agent = ReactAgent(model=model, tools=search_tools)\n'
        'else:\n'
        '    mock = mock_llm("TOOL: search, args: {\\"query\\": \\"default\\"}")\n'
        '    agent = ReactAgent(model=mock, tools=search_tools)\n'
        '\n'
        'for question in ["What is agentic AI?", "Tell me about Python", "What is PBL?"]:\n'
        '    print(f">>> {question}")\n'
        '    print(agent.run(question))\n'
        '    print()\n'
    ),

    md(
        '### Silver — Add Your Own Tool\n'
        '\n'
        'Add a new tool to the agent. Write a function and register it with `make_tool`. '
        'Make it domain-relevant (e.g., a biotech lookup for Alejandro, a risk calculator for Jošt).'
    ),
    code(
        '# --- Write your tool function ---\n'
        'def my_custom_tool(param):\n'
        '    """Describe what your tool does."""\n'
        '    # Your logic here\n'
        '    return f"Processed: {param}"\n'
        '# ---------------------------------\n'
        '\n'
        'custom_tools = [\n'
        '    make_tool("calculator", "Evaluate math expressions", calculator),\n'
        '    make_tool("my_tool", "Description of your tool", my_custom_tool),\n'
        ']\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    model = make_model(client, cfg["model"], system_prompt_tools=custom_tools)\n'
        '    agent = ReactAgent(model=model, tools=custom_tools)\n'
        '    result = agent.run("Test my custom tool")\n'
        '    print("Agent response:")\n'
        '    print(result)\n'
        'else:\n'
        '    print(f"Tool registered: my_custom_tool")\n'
        '    print("In real mode, the agent would call your tool.")\n'
    ),

    md(
        '### Gold — Implement ReactAgent From Scratch\n'
        '\n'
        'Write your own agent loop without importing from `agent_helpers`. '
        'It must handle: max_steps, tool parsing, tool execution, and graceful failure.'
    ),
    code(
        '# --- Implement your own ReactAgent ---\n'
        'class MyAgent:\n'
        '    def __init__(self, model, tools, max_steps=5):\n'
        '        self.model = model\n'
        '        self.tools = {t["name"]: t for t in tools}\n'
        '        self.history = []\n'
        '        self.max_steps = max_steps\n'
        '\n'
        '    def run(self, user_input):\n'
        '        # Implement the agent loop\n'
        '        # Steps: for each step, call self.model(), check if it wants a tool,\n'
        '        # execute tool, add observation to history, or return final answer\n'
        '        pass  # Replace with your implementation\n'
        '# --------------------------------------\n'
        '\n'
        '# Test your implementation\n'
        'if not use_mock and client is not None:\n'
        '    model = make_model(client, cfg["model"])\n'
        '    my_agent = MyAgent(model=model, tools=tools)\n'
        '    result = my_agent.run("What is 2 + 2?")\n'
        '    print("MyAgent result:", result)\n'
        'else:\n'
        '    print("Implement the run method, then test with real API.")\n'
        '    print("Compare your implementation with agent_helpers.ReactAgent.")\n'
    ),

    # ---- Exit link ----
    md(
        '## Next Steps\n'
        '\n'
        'You\'ve built an agent loop. You understand the core pattern: '
        'model decides → tool executes → agent observes → repeat.\n'
        '\n'
        '**Next notebook:** `02_memory_and_rag.ipynb` — "The Agent\'s Mind"\n'
        '\n'
        '> "What happens when the agent needs to remember what it learned 20 turns ago?"\n'
    ),
]


notebook = {
    "cells": ALL_CELLS,
    "metadata": {
        "kernelspec": KERNEL_SPEC,
        "language_info": LANG_INFO,
    },
    "nbformat": NB_VERSION,
    "nbformat_minor": NB_MINOR,
}

out_path = os.path.join(os.path.dirname(__file__), "01_agent_loop.ipynb")
with open(out_path, "w") as f:
    json.dump(notebook, f, indent=2)

print(f"Generated: {out_path}")
print(f"Cells: {len(ALL_CELLS)} ({sum(1 for c in ALL_CELLS if c['cell_type']=='markdown')} markdown, {sum(1 for c in ALL_CELLS if c['cell_type']=='code')} code)")
