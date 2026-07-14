"""Generate notebooks/05_building_tools.ipynb"""

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


ALL_CELLS = [
    md(
        '# Notebook 05: Custom Tools & Multi-Agent Systems\n'
        '\n'
        '*Advanced / Optional — Complexity Ladder Level 3-4*\n'
        '\n'
        'You\'ve mastered the agent loop, memory, planning, and reflection. '
        'Now we connect agents to the outside world through standardized tools (MCP) '
        'and explore how multiple agents collaborate.\n'
        '\n'
        '**Expected time:** ~60 minutes\n'
        '**Prerequisites:** All prior notebooks\n'
    ),

    md(
        '## What You\'ll Learn\n'
        '\n'
        '1. When and why to build custom tools (vs. using libraries)\n'
        '2. MCP (Model Context Protocol) — the "USB-C for AI"\n'
        '3. Build an MCP server with resources, tools, and prompts\n'
        '4. Connect an MCP server to an agent\n'
        '5. Multi-agent supervisor routing: one agent delegates to specialists\n'
        '6. Multi-agent debate pattern: agents challenge each other\n'
    ),

    md(
        '## Setup\n'
        '\n'
        'This notebook has two modes:\n'
        '- **Full mode** (USE_MCP = True): Install `mcp` SDK, run a real server\n'
        '- **Concept mode** (USE_MCP = False): Pure Python simulation, no extra deps'
    ),
    code(
        '!pip install mcp openai==1.68.2  # optional: only needed for MCP full mode\n'
        '\n'
        'USE_MCP = False  # Set True if you can install the mcp SDK\n'
        '\n'
        'from agent_helpers import ReactAgent, make_tool, mock_llm\n'
        'import os\n'
        'import getpass\n'
        'import json\n'
        'from pathlib import Path\n'
        '\n'
        'print("MCP mode:", "ON (full)" if USE_MCP else "Concept (pure Python)")\n'
        '\n'
        '# --- Optional .env file loading ---\n'
        'env_path = Path.cwd() / ".env"\n'
        'if env_path.exists():\n'
        '    with open(env_path) as f:\n'
        '        for line in f:\n'
        '            line = line.strip()\n'
        '            if line and not line.startswith("#") and "=" in line:\n'
        '                k, v = line.split("=", 1)\n'
        '                os.environ.setdefault(k.strip(), v.strip())\n'
        '    print("Loaded .env file.")\n'
        'else:\n'
        '    print("No .env file found — you will be prompted for API keys.")\n'
        '\n'
        '# --- Provider config (for supervisor/debate patterns with real LLM) ---\n'
        'PROVIDER = "openrouter"  # Choose: openrouter, groq, openai\n'
        '\n'
        'MOCK = {\n'
        '    "openrouter": True,\n'
        '    "groq":       True,\n'
        '    "openai":     True,\n'
        '}\n'
        '\n'
        'KEY_ENV_VAR = {\n'
        '    "openrouter": "OPENROUTER_API_KEY",\n'
        '    "groq":       "GROQ_API_KEY",\n'
        '    "openai":     "OPENAI_API_KEY",\n'
        '}\n'
        '\n'
        'CONFIG = {\n'
        '    "openrouter": {\n'
        '        "name": "OpenRouter",\n'
        '        "model": "deepseek/deepseek-v4-flash",\n'
        '        "base_url": "https://openrouter.ai/api/v1",\n'
        '        "key_url": "https://openrouter.ai/keys",\n'
        '    },\n'
        '    "groq": {\n'
        '        "name": "Groq",\n'
        '        "model": "openai/gpt-oss-20b",\n'
        '        "base_url": "https://api.groq.com/openai/v1",\n'
        '        "key_url": "https://console.groq.com/keys",\n'
        '    },\n'
        '    "openai": {\n'
        '        "name": "OpenAI",\n'
        '        "model": "gpt-4o-mini",\n'
        '        "base_url": None,\n'
        '        "key_url": "https://platform.openai.com/api-keys",\n'
        '    },\n'
        '}\n'
        '\n'
        'cfg = CONFIG[PROVIDER]\n'
        'use_mock = MOCK[PROVIDER]\n'
        '\n'
        'if use_mock:\n'
        '    print(f"[{cfg[\'name\']}] Mock mode enabled. Supervisor/debate will use canned responses.")\n'
        '    client = None\n'
        'else:\n'
        '    from openai import OpenAI\n'
        '    api_key = os.environ.get(KEY_ENV_VAR[PROVIDER]) or getpass.getpass(f"Enter your {cfg[\'name\']} API key: ")\n'
        '    kwargs = {"api_key": api_key}\n'
        '    if cfg["base_url"]:\n'
        '        kwargs["base_url"] = cfg["base_url"]\n'
        '    client = OpenAI(**kwargs)\n'
        '    print(f"[{cfg[\'name\']}] API key configured. Model: {cfg[\'model\']}")\n'
    ),

    md(
        '## 1. When to Build Custom Tools\n'
        '\n'
        'Not every problem needs a custom tool. Build one when:\n'
        '\n'
        '| Use Case | Example | Use Library or Build Tool? |\n'
        '|----------|---------|---------------------------|\n'
        '| Public API exists | Weather, search, currency | Use library directly |\n'
        '| Internal/private data | Company DB, proprietary API | **Build tool wrapper** |\n'
        '| Custom computation | Domain-specific calculation | **Build tool** |\n'
        '| Hardware control | Arduino, sensors, robotic arm | **Build tool** |\n'
        '| No standard interface exists | Legacy system | **Build tool + MCP** |\n'
    ),

    md(
        '## 2. MCP — Model Context Protocol\n'
        '\n'
        'MCP is a standard for connecting AI applications to external systems. '
        'Think of it as "USB-C for AI" — one protocol that works across models and tools.\n'
        '\n'
        '```mermaid\n'
        'graph LR\n'
        '    A[LLM Host] <--> B[MCP Server]\n'
        '    B --> C[Resource: file]\n'
        '    B --> D[Tool: calculator]\n'
        '    B --> E[Prompt: summarize]\n'
        '```\n'
        '\n'
        'Three building blocks:\n'
        '- **Resource**: Readable data (files, DB queries)\n'
        '- **Tool**: Action the model can invoke (functions)\n'
        '- **Prompt**: Reusable prompt template\n'
    ),

    md(
        '### MCP Server in Python (Full Mode)\n'
        '\n'
        'If `USE_MCP = True`, this code builds a running MCP server. '
        'It requires the `mcp` package.'
    ),
    code(
        'if USE_MCP:\n'
        '    from mcp import Server, Resource, Tool\n'
        '\n'
        '    server = Server("agentic-course-server")\n'
        '\n'
        '    @server.resource(uri="file:///notes", name="course_notes")\n'
        '    def read_notes() -> str:\n'
        '        return "Agentic AI uses planning, memory, tools, and reflection."\n'
        '\n'
        '    @server.tool(name="calculator", description="Evaluate math expressions")\n'
        '    def calculator(expr: str) -> str:\n'
        '        try:\n'
        '            return str(eval(expr))\n'
        '        except Exception as e:\n'
        '            return f"Error: {e}"\n'
        '\n'
        '    @server.prompt(name="summarize", description="Summarize a topic")\n'
        '    def summarize(topic: str) -> str:\n'
        '        return f"Please provide a concise summary of {topic}."\n'
        '\n'
        '    print("MCP server defined.")\n'
        '    print("  Resources: file:///notes")\n'
        '    print("  Tools: calculator")\n'
        '    print("  Prompts: summarize")\n'
        '    print("\\nTo run: from mcp import run; run(server)")\n'
        'else:\n'
        '    print("Set USE_MCP = True at the top to see the real SDK code.")\n'
        '    print("Below is the conceptual equivalent in pure Python.")\n'
    ),

    md(
        '### MCP Server (Concept Mode — Pure Python)\n'
        '\n'
        'This simulates the same pattern without the MCP SDK. '
        'The structure is the same: resources, tools, prompts.'
    ),
    code(
        'class MCPServer:\n'
        '    """Minimal MCP-like server. Same concepts, no SDK dependency."""\n'
        '    def __init__(self, name):\n'
        '        self.name = name\n'
        '        self.resources = {}\n'
        '        self.tools = {}\n'
        '        self.prompts = {}\n'
        '\n'
        '    def add_resource(self, uri, name, fn):\n'
        '        self.resources[uri] = {"name": name, "fn": fn}\n'
        '\n'
        '    def add_tool(self, name, description, fn):\n'
        '        self.tools[name] = {"description": description, "fn": fn}\n'
        '\n'
        '    def add_prompt(self, name, description, template_fn):\n'
        '        self.prompts[name] = {"description": description, "fn": template_fn}\n'
        '\n'
        '    def get_resource(self, uri):\n'
        '        r = self.resources.get(uri)\n'
        '        if r:\n'
        '            return r["fn"]()\n'
        '        return f"Resource not found: {uri}"\n'
        '\n'
        '    def call_tool(self, name, **kwargs):\n'
        '        t = self.tools.get(name)\n'
        '        if t:\n'
        '            return t["fn"](**kwargs)\n'
        '        return f"Tool not found: {name}"\n'
        '\n'
        '    def get_prompt(self, name, **kwargs):\n'
        '        p = self.prompts.get(name)\n'
        '        if p:\n'
        '            return p["fn"](**kwargs)\n'
        '        return f"Prompt not found: {name}"\n'
        '\n'
        '    def list(self):\n'
        '        print(f"Server: {self.name}")\n'
        '        print(f"  Resources: {list(self.resources)}")\n'
        '        print(f"  Tools: {list(self.tools)}")\n'
        '        print(f"  Prompts: {list(self.prompts)}")\n'
        '\n'
        'print("MCPServer class defined.")\n'
    ),

    md(
        '### Build a Domain-Specific MCP Server\n'
        '\n'
        'Let\'s build a server relevant to your PBL project. '
        'It combines data, actions, and reusable prompts.'
    ),
    code(
        'server = MCPServer("my-project-server")\n'
        '\n'
        '# Resource: domain knowledge\n'
        'server.add_resource("file:///domain", "domain_knowledge",\n'
        '    lambda: "Agentic AI systems use loops, memory, planning, and reflection. "\n'
'        "The Complexity Ladder ranges from Level 1 (simple tool use) to Level 4 (multi-agent).")\n'
        '\n'
        '# Resource: project notes\n'
        'def read_project_notes():\n'
        '    return ("Project goal: Build an agent that automates literature review. "\n'
'        "Key features: search papers, extract findings, generate summary.")\n'
        'server.add_resource("file:///project-notes", "project_notes", read_project_notes)\n'
        '\n'
        '# Tool: search domain knowledge\n'
        'def domain_search(query):\n'
        '    db = {\n'
        '        "agent loop": "Plan -> Act -> Observe -> Adapt cycle.",\n'
        '        "memory": "Short-term (context) and long-term (RAG) storage.",\n'
        '        "planning": "Task decomposition into sub-steps.",\n'
        '        "reflection": "Self-critique and iterative improvement.",\n'
        '    }\n'
        '    return db.get(query.lower(), f"No entry for: {query}")\n'
        'server.add_tool("search", "Search course concepts", domain_search)\n'
        '\n'
        '# Tool: to-do manager\n'
        'todos = []\n'
        'def add_todo(item):\n'
        '    todos.append(item)\n'
        '    return f"Added: {item} (total: {len(todos)})"\n'
        'def list_todos():\n'
        '    return "\\n".join(f"  {i+1}. {t}" for i, t in enumerate(todos)) if todos else "  (empty)"\n'
        'server.add_tool("add_todo", "Add a to-do item", add_todo)\n'
        'server.add_tool("list_todos", "List all to-do items", list_todos)\n'
        '\n'
        '# Prompt: project reflection\n'
        'def reflection_prompt(progress):\n'
        '    return f"Given my progress: {progress}, what should I do next on my project?"\n'
        'server.add_prompt("project_reflection", "Reflect on project progress", reflection_prompt)\n'
        '\n'
        'server.list()\n'
    ),

    md(
        '### Using the MCP Server from an Agent\n'
        '\n'
        'The agent doesn\'t call the MCP server directly. Instead, '
        'each tool in the MCP server becomes a tool the agent can use.'
    ),
    code(
        'from agent_helpers import ReactAgent, make_tool\n'
        '\n'
        'mcp_tools = [\n'
        '    make_tool("search", "Search domain concepts", lambda q: server.call_tool("search", query=q)),\n'
        '    make_tool("add_todo", "Add a to-do item", lambda i: server.call_tool("add_todo", item=i)),\n'
        ']\n'
        '\n'
        '# With real API\n'
        'if not USE_MCP:\n'
        '    # Use mock for concept demo\n'
        '    mock = mock_llm("TOOL: search, args: {\\"query\\": \\"agent loop\\"}")\n'
        '    agent = ReactAgent(model=mock, tools=mcp_tools)\n'
        '    result = agent.run("Search for agent loop concepts")\n'
        '    print("Agent with MCP tools:")\n'
        '    print(result)\n'
        '    print("\\nMCP server tools are used through the same agent interface.")\n'
        'else:\n'
        '    print("In full MCP mode, the server runs in a separate process.")\n'
        '    print("The agent connects via stdio or SSE transport.")\n'
    ),

    md(
        '## 3. Multi-Agent: Supervisor Routing\n'
        '\n'
        'One agent (the supervisor) receives a task, decides which specialist '
        'agent should handle it, and routes the work.\n'
        '\n'
        '```mermaid\n'
        'graph TD\n'
        '    S[Supervisor] -->|research task| R[Research Agent]\n'
        '    S -->|writing task| W[Writer Agent]\n'
        '    S -->|quality check| Q[Quality Agent]\n'
        '    R --> S\n'
        '    W --> S\n'
        '    Q --> S\n'
        '    S -->|final| U[User]\n'
        '```'
    ),
    code(
        'class SpecialistAgent:\n'
        '    """A simple agent with a specific role."""\n'
        '    def __init__(self, name, role_desc, model_fn):\n'
        '        self.name = name\n'
        '        self.role = role_desc\n'
        '        self.model = model_fn\n'
        '\n'
        '    def handle(self, task):\n'
        '        return self.model([{"role": "user", "content": (\n'
        '            f"You are a {self.role}. Respond to: {task}"\n'
        '        )}])\n'
        '\n'
        'class Supervisor:\n'
        '    """Routes tasks to specialist agents."""\n'
        '    def __init__(self, model_fn):\n'
        '        self.model = model_fn\n'
        '        self.specialists = {}\n'
        '\n'
        '    def register(self, name, agent):\n'
        '        self.specialists[name] = agent\n'
        '\n'
        '    def run(self, task):\n'
        '        # Decide which specialist to use\n'
        '        decision = self.model([{"role": "user", "content": (\n'
        '            f"Available specialists: {list(self.specialists)}.\\n"\n'
        '            f"Which should handle: {task}\\nReply with just the name."\n'
        '        )}])\n'
        '\n'
        '        chosen = decision.strip().lower()\n'
        '        agent = self.specialists.get(chosen)\n'
        '\n'
        '        if agent:\n'
        '            print(f"Supervisor delegates to: {agent.name}")\n'
        '            result = agent.handle(task)\n'
        '            return self.model([{"role": "user", "content": (\n'
        '                f"Task: {task}\\nResult from {agent.name}: {result}\\n"\n'
        '                f"Format a final response for the user:"\n'
        '            )}])\n'
        '        else:\n'
        '            return f"No specialist available for: {chosen}"\n'
        '\n'
        'if not USE_MCP:\n'
        '    mock = mock_llm()\n'
        '    research = SpecialistAgent("researcher", "research specialist who finds information", mock)\n'
        '    writer = SpecialistAgent("writer", "technical writer who explains clearly", mock)\n'
        '    qa = SpecialistAgent("qa", "quality assurance specialist who checks for errors", mock)\n'
        '\n'
        '    sup = Supervisor(mock)\n'
        '    sup.register("researcher", research)\n'
        '    sup.register("writer", writer)\n'
        '    sup.register("qa", qa)\n'
        '\n'
        '    print("Supervisor routing system ready.")\n'
        '    print("  Specialists: researcher, writer, qa")\n'
        '    print("  Task: the supervisor decides who handles each request.")\n'
        'else:\n'
        '    print("Supervisor system defined. Register specialists and call .run(task).")\n'
    ),

    md(
        '### Run the Supervisor\n'
    ),
    code(
        'if not USE_MCP:\n'
        '    for task in ["Find latest research on agentic AI", "Write a summary", "Check this text for errors"]:\n'
        '        print(f">>> {task}")\n'
        '        result = sup.run(task)\n'
        '        print(f"  Final: {result[:80]}...\\n")\n'
        'else:\n'
        '    print("Run with real API to see supervisor routing in action.")\n'
    ),

    md(
        '## 4. Multi-Agent: Debate Pattern\n'
        '\n'
        'Two agents take opposing positions on a question. A meta-agent judges '
        'the arguments and produces a balanced conclusion.\n'
        '\n'
        '```mermaid\n'
        'graph TD\n'
        '    Q[Question] --> A[Agent 1: Pro]\n'
        '    Q --> B[Agent 2: Con]\n'
        '    A --> J[Judge]\n'
        '    B --> J\n'
        '    J --> C[Conclusion]\n'
        '```'
    ),
    code(
        'class Debate:\n'
        '    """Two agents debate, a judge decides."""\n'
        '    def __init__(self, model_fn):\n'
        '        self.model = model_fn\n'
        '\n'
        '    def run(self, question, position_a, position_b):\n'
        '        print(f"Question: {question}\\n")\n'
        '\n'
        '        arg_a = self.model([{"role": "user", "content": (\n'
        '            f"Argue FOR this position: {position_a}\\n"\n'
        '            f"In context of: {question}"\n'
        '        )}])\n'
        '        print(f"--- Agent A (FOR: {position_a}) ---")\n'
        '        print(f"{arg_a[:150]}...\\n")\n'
        '\n'
        '        arg_b = self.model([{"role": "user", "content": (\n'
        '            f"Argue AGAINST this position: {position_a}\\n"\n'
        '            f"In context of: {question}"\n'
        '        )}])\n'
        '        print(f"--- Agent B (AGAINST: {position_a}) ---")\n'
        '        print(f"{arg_b[:150]}...\\n")\n'
        '\n'
        '        verdict = self.model([{"role": "user", "content": (\n'
        '            f"Question: {question}\\n"\n'
        '            f"Argument FOR: {arg_a}\\n"\n'
        '            f"Argument AGAINST: {arg_b}\\n"\n'
        '            f"Provide a balanced conclusion that weighs both sides:"\n'
        '        )}])\n'
        '        print("=== JUDGE\'S VERDICT ===")\n'
        '        print(verdict)\n'
        '        return verdict\n'
        '\n'
        'print("Debate class defined.")\n'
    ),

    md(
        '### Run a Debate\n'
    ),
    code(
        'if not USE_MCP:\n'
        '    debate = Debate(mock_llm())\n'
        '    debate.run(\n'
        '        "Should AI agents operate autonomously without human approval?",\n'
        '        "Full autonomy increases efficiency and speed",\n'
        '        "Human oversight ensures safety and accountability"\n'
        '    )\n'
        'else:\n'
        '    print("Run with real API to see the debate pattern.")\n'
    ),

    md(
        '## Combining MCP with Multi-Agent\n'
        '\n'
        'In a real system, MCP servers provide the tools that specialist agents use. '
        'Each specialist connects to its own MCP server:\n'
        '\n'
        '```mermaid\n'
        'graph TD\n'
        '    S[Supervisor] --> R[Research Agent]\n'
        '    S --> W[Writer Agent]\n'
        '    R --> M1[MCP: Search DB]\n'
        '    W --> M2[MCP: Document Store]\n'
        '```\n'
        '\n'
        'This architecture scales to complex systems while keeping components modular.'
    ),

    md(
        '## What Breaks?\n'
    ),

    md(
        '### Break 1: MCP Transport Mismatch\n'
        '\n'
        'MCP supports stdio (same process), SSE (server-sent events), and HTTP. '
        'If the host expects one transport and the server provides another, '
        'they can\'t communicate.'
    ),
    code(
        'print("Transport mismatch scenarios:")\n'
        'print("  Host uses SSE but server runs on stdio -> connection refused")\n'
        'print("  Server runs on HTTP but host expects SSE -> protocol error")\n'
        'print("  Port already in use -> bind error")\n'
        'print("\\nFix: Verify transport type in both host config and server config.")\n'
    ),

    md(
        '### Break 2: MCP Version Mismatch\n'
        '\n'
        'The MCP protocol is evolving. A v0.1 server won\'t work with a v0.2 host.'
    ),
    code(
        'print("Version mismatch:")\n'
        'print("  Server SDK: 0.1.0, Host SDK: 0.2.0")\n'
        'print("  -> Handshake failure during initialization")\n'
        'print("\\nFix: Pin versions in requirements.txt. Use compatible SDK versions.")\n'
    ),

    md(
        '### Break 3: Supervisor Can\'t Decide\n'
        '\n'
        'If the supervisor can\'t classify a task, it may route to the wrong specialist '
        'or fail to route at all.'
    ),
    code(
        'def confused_supervisor(task, model_fn):\n'
        '    """Demonstrates a supervisor that can\'t decide."""\n'
        '    decision = model_fn([{"role": "user", "content": (\n'
        '        f"Specialists: [researcher, writer, qa]. Which handles: {task}\\n"\n'
        '        f"If unsure, reply: UNKNOWN"\n'
        '    )}])\n'
        '    if "UNKNOWN" in decision:\n'
        '        print(f"Supervisor confused by: {task}")\n'
        '        print("Fix: Add more specific routing rules or a default specialist.")\n'
        '    else:\n'
        '        print(f"Routed to: {decision.strip()}")\n'
        '\n'
        'if not USE_MCP:\n'
        '    confused_supervisor("Do the thing with the stuff", mock_llm())\n'
        'else:\n'
        '    print("Mock — supervisor confusion demo.")\n'
    ),

    md(
        '### Break 4: Debate Never Converges\n'
        '\n'
        'If the two agents argue different interpretations without acknowledging '
        'the other side, the judge can\'t produce a balanced conclusion.'
    ),
    code(
        'print("Debate convergence failure:")\n'
        'print("  Agent A: \\"AI should be fully autonomous because...\\"")\n'
        'print("  Agent B: \\"AI should never be autonomous because...\\"")\n'
        'print("  Judge: Can\'t reconcile absolute positions")\n'
        'print("\\nFix: Instruct agents to acknowledge the other side. ")\n'
        'print("  Use: \\"Argue FOR this position, but also address the strongest counterargument.\\"")\n'
    ),

    md(
        '## Connection to Agentic AI\n'
        '\n'
        'This notebook covers **Complexity Ladder Level 4**: '
        'Multiple cooperating agents or persistent state across long tasks.\n'
        '\n'
        '**Marking Grid alignment:**\n'
        '- **Solution**: MCP-based architecture shows professional tool design\n'
        '- **Demo**: Show how your agent handles failures gracefully\n'
        '- **Presentation**: Multi-agent patterns demonstrate deep understanding\n'
        '\n'
        '> "If you can explain WHY you chose Level 2 over Level 4, '
        'that\'s better than building a broken Level 4."\n'
        '> — Course mantra\n'
    ),

    md(
        '### PBL Reflection\n'
    ),
    code(
        'print("Think about YOUR project:")\n'
        'print("  1. Do you need an MCP server? Or is a simple tool wrapper enough?")\n'
        'print("  2. Would your project benefit from multiple specialists or is one agent enough?")\n'
'print("  3. The course mantra: does your Complexity Ladder choice match your team\'s skills?")\n'
'print("  4. What\'s your fallback if you aim for Level 4 but run out of time?")\n'
        'print("\\nThe best project is one that WORKS, at any level of the ladder.")\n'
    ),

    md(
        '## Exercises\n'
    ),

    md(
        '### Bronze — Run the MCP Server\n'
        '\n'
        'Run the MCPServer code above with different resources and tools '
        'relevant to your domain. List what\'s registered.'
    ),
    code(
        '# Build a server for YOUR domain\n'
        'my_server = MCPServer("my-project")\n'
        'my_server.add_resource("file:///kb", "knowledge_base",\n'
        '    lambda: "Domain-specific knowledge goes here.")\n'
        'my_server.add_tool("my_tool", "Describe your domain tool",\n'
        '    lambda q: f"Processed domain query: {q}")\n'
        'my_server.list()\n'
    ),

    md(
        '### Silver — Add a Custom Tool to the MCP Server\n'
        '\n'
        'Add a domain-specific tool to the MCPServer. '
        'For example: a PubMed search tool (Alejandro), a risk calculator (Jost), '
        'a schedule planner (Stamatela), or a cognitive load analyzer (Melike).'
    ),
    code(
        '# --- Your domain tool ---\n'
        'def your_domain_tool(param):\n'
        '    """Implement your domain-specific logic."""\n'
        '    # Example: query a database, run a calculation, search an API\n'
        '    return f"Domain result for: {param}"\n'
        '# -------------------------\n'
        '\n'
        'my_server.add_tool("domain_tool", "Description of your domain tool", your_domain_tool)\n'
        'print("Custom tool added.")\n'
        'print(my_server.call_tool("domain_tool", param="test input"))\n'
    ),

    md(
        '### Gold — Supervisor with Two MCP Servers\n'
        '\n'
        'Build two MCP servers (e.g., one for research, one for writing). '
        'Create a supervisor that routes tasks to the appropriate server. '
        'This is a full Level 4 architecture.'
    ),
    code(
        '# MCP Server 1: Research\n'
        'research_server = MCPServer("research-server")\n'
        'research_server.add_tool("search_papers", "Search academic papers",\n'
        '    lambda q: f"Found papers about: {q}")\n'
        'research_server.add_tool("summarize_paper", "Summarize a paper",\n'
        '    lambda t: f"Summary of: {t}")\n'
        '\n'
        '# MCP Server 2: Writing\n'
        'writing_server = MCPServer("writing-server")\n'
        'writing_server.add_tool("draft", "Draft text",\n'
        '    lambda t: f"Draft: {t}")\n'
        'writing_server.add_tool("format", "Format output",\n'
        '    lambda t: f"Formatted:\\n{t}")\n'
        '\n'
        '# Create specialist agents\n'
        'class SpecialistAgent:\n'
        '    def __init__(self, name, server):\n'
        '        self.name = name\n'
        '        self.server = server\n'
        '\n'
        '    def handle(self, task):\n'
        '        tool_name = "search_papers"\n'
        '        if "search" in task.lower() or "find" in task.lower():\n'
        '            tool_name = "search_papers"\n'
        '        else:\n'
        '            tool_name = list(self.server.tools.keys())[0]\n'
        '        kwargs = {"q": task} if "search" in task.lower() else {"t": task}\n'
        '        return self.server.call_tool(tool_name, **kwargs)\n'
        '\n'
        'researcher = SpecialistAgent("researcher", research_server)\n'
        'writer = SpecialistAgent("writer", writing_server)\n'
        '\n'
        '# Supervisor routes tasks\n'
        'def supervisor_route(task, model_fn):\n'
        '    decision = model_fn([{\"role\": \"user\", \"content\": (\n'
        '        f"Task: {task}\\nAvailable: researcher, writer\\n"\n'
        '        f"Reply with just the name."\n'
        '    )}])\n'
        '    chosen = decision.strip().lower()\n'
        '    if chosen == "researcher":\n'
        '        print("-> Research Server")\n'
        '        return researcher.handle(task)\n'
        '    elif chosen == "writer":\n'
        '        print("-> Writing Server")\n'
        '        return writer.handle(task)\n'
        '    return f"No server for: {chosen}"\n'
        '\n'
        'print("Two-server system defined.")\n'
        'print("Supervisor routes: find papers -> research server, write -> writing server")\n'
    ),

    md(
        '## Next Steps\n'
        '\n'
        'This is the final notebook. You now have the complete toolkit:\n'
        '\n'
        '| Notebook | Skill | Ladder Level |\n'
        '|----------|-------|-------------|\n'
        '| 00 | Environment + first API call | — |\n'
        '| 01 | Agent loop | Level 1 |\n'
        '| 02 | Memory & RAG | Level 1-2 |\n'
        '| 03 | Planning | Level 2-3 |\n'
        '| 04 | Reflection | Level 2-3 |\n'
        '| 05 | Custom tools & Multi-agent | Level 3-4 |\n'
        '\n'
        '> "A well-executed Level 1 project beats a broken Level 4 one. '
        'Choose your level, justify it, and build something that works."\n'
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

out_path = os.path.join(os.path.dirname(__file__), "05_building_tools.ipynb")
with open(out_path, "w") as f:
    json.dump(notebook, f, indent=2)

print(f"Generated: {out_path}")
print(f"Cells: {len(ALL_CELLS)} ({sum(1 for c in ALL_CELLS if c['cell_type']=='markdown')} md, {sum(1 for c in ALL_CELLS if c['cell_type']=='code')} code)")
