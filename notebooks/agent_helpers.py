"""Agentic AI course helper module.

Pre-built classes for notebooks 01-05.
Students import and use before implementing from scratch.

Provides:
    ReactAgent: Pre-built agent loop
    Memory: Conversation memory with running summary
    simple_rag: Single-function keyword retrieval
    mock_llm: Canned response for offline/API-failure use
    mock_search: Predefined search results
    make_tool: Tool definition factory
    safe_calc: Safe arithmetic evaluator (use instead of eval)
"""

import inspect
import json
from typing import Any, Callable


def tools_to_openai_native(tools: list[dict]) -> list[dict]:
    """Convert make_tool dicts to OpenAI native tools format."""
    native = []
    for t in tools:
        sig = inspect.signature(t["fn"])
        props = {}
        for pname, param in sig.parameters.items():
            props[pname] = {"type": "string", "description": f"The {pname} parameter"}

        native.append({
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": {
                    "type": "object",
                    "properties": props,
                    "required": list(sig.parameters.keys()),
                }
            }
        })
    return native


class ReactAgent:
    """Agent loop: Thought -> Action -> Observation -> repeat."""

    def __init__(self, model: Callable, tools: list[dict], max_steps: int = 5, system_prompt: str | None = None):
        self.model = model
        self.tools = {t["name"]: t for t in tools}
        self.history = []
        self.max_steps = max_steps
        self.system_prompt = system_prompt

    def run(self, user_input: str) -> str:
        messages = list(self.history) + [{"role": "user", "content": user_input}]

        for step in range(self.max_steps):
            msgs = list(messages)
            if self.system_prompt:
                msgs = [{"role": "system", "content": self.system_prompt}] + msgs

            response = self.model(msgs)

            if isinstance(response, dict):
                if response.get("type") == "tool_call":
                    tool_name = response["name"]
                    tool_args = response["args"]
                    tool_call_id = response["tool_call_id"]
                    try:
                        result = self._execute_tool(tool_name, tool_args)
                    except Exception as e:
                        result = f"Error executing tool '{tool_name}': {e}"
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": tool_call_id,
                            "type": "function",
                            "function": {
                                "name": tool_name,
                                "arguments": json.dumps(tool_args),
                            }
                        }]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": str(result),
                    })
                    self.history = list(messages)
                    continue

                if response.get("type") == "text":
                    self.history = list(messages)
                    return response["content"]

            if isinstance(response, str) and "TOOL:" in response:
                messages.append({"role": "assistant", "content": response})
                tool_name, tool_args = self._parse_tool_call(response)
                try:
                    result = self._execute_tool(tool_name, tool_args)
                except Exception as e:
                    result = f"Error executing tool '{tool_name}': {e}"
                messages.append({"role": "tool", "content": str(result)})
                self.history = list(messages)
                continue

            text = response.get("content") if isinstance(response, dict) else str(response)
            self.history = list(messages)
            return text

        return "Max steps reached"

    def _parse_tool_call(self, response: str) -> tuple[str, dict]:
        parts = response.replace("TOOL:", "").strip().split(", args:")
        name = parts[0].strip()
        if len(parts) > 1:
            try:
                args = json.loads(parts[1])
            except json.JSONDecodeError:
                args = {}
        else:
            args = {}
        return name, args

    def _execute_tool(self, name: str, args: dict) -> Any:
        tool = self.tools.get(name)
        if not tool:
            return f"Error: tool '{name}' not found. Available: {list(self.tools)}"
        return tool["fn"](**args)


class Memory:
    """Conversation memory with automatic summarization on overflow."""

    def __init__(self, max_messages: int = 10):
        self.messages = []
        self.max_messages = max_messages
        self.summary = ""

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) >= self.max_messages:
            self._summarize()

    def get_context(self) -> list[dict]:
        if self.summary:
            prefix = {"role": "system", "content": f"Summary of earlier conversation: {self.summary}"}
            return [prefix] + self.messages[-3:]
        return self.messages

    def _summarize(self):
        text = " ".join(m["content"] for m in self.messages)
        self.summary = text[:200] + "..." if len(text) > 200 else text
        self.messages = self.messages[-3:]


def simple_rag(query: str, documents: list[str], k: int = 3) -> str:
    """Keyword-based retrieval (no embeddings, works offline)."""
    query_words = set(query.lower().split())
    scored = []
    for i, doc in enumerate(documents):
        doc_words = set(doc.lower().split())
        score = len(query_words & doc_words)
        scored.append((score, i, doc))
    scored.sort(key=lambda x: (-x[0], x[1]))
    top = [doc for _, _, doc in scored[:k]]
    return "\n---\n".join(top)


def mock_llm(response: str = "Default mock response.") -> Callable:
    """Return a mock LLM that always returns a canned response."""
    def _mock(history: list[dict]) -> str:
        msgs = [m["content"] for m in history if m["role"] == "user"]
        last = msgs[-1] if msgs else ""
        if "weather" in last.lower():
            return "TOOL: get_weather, args: {}"
        if "calc" in last.lower() or "math" in last.lower():
            return "TOOL: calculator, args: {\"expr\": \"" + last + "\"}"
        return response
    return _mock


def mock_search(query: str, results: list[str] | None = None) -> str:
    """Return predefined search results."""
    default = [
        "Agentic AI systems use perception-reasoning-action loops.",
        "The ReAct pattern interleaves reasoning traces with tool use.",
        "Memory separates one-shot LLM calls from persistent agents.",
    ]
    hits = results or default
    return "\n".join(hits[:3])



def safe_calc(expr: str) -> str:
    """Safely evaluate arithmetic expressions without using eval().

    Supports: +, -, *, /, **, %, unary minus/plus, integer and float literals.
    Use this instead of eval() for calculator tools — eval() allows arbitrary
    code execution which is a security risk in agentic systems.
    """
    import ast as _ast
    import operator as _op
    _ops = {
        _ast.Add: _op.add, _ast.Sub: _op.sub,
        _ast.Mult: _op.mul, _ast.Div: _op.truediv,
        _ast.Pow: _op.pow, _ast.Mod: _op.mod,
        _ast.USub: _op.neg, _ast.UAdd: _op.pos,
    }
    def _ev(n):
        if isinstance(n, _ast.Constant):
            if not isinstance(n.value, (int, float)):
                raise ValueError("Only numeric literals allowed")
            return n.value
        if isinstance(n, _ast.BinOp):
            fn = _ops.get(type(n.op))
            if fn is None:
                raise ValueError(f"Unsupported operator: {type(n.op).__name__}")
            return fn(_ev(n.left), _ev(n.right))
        if isinstance(n, _ast.UnaryOp):
            fn = _ops.get(type(n.op))
            if fn is None:
                raise ValueError(f"Unsupported operator: {type(n.op).__name__}")
            return fn(_ev(n.operand))
        raise ValueError(f"Unsupported expression: {type(n).__name__}")
    try:
        result = _ev(_ast.parse(expr.strip(), mode="eval").body)
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def make_tool(name: str, description: str, fn: Callable) -> dict:
    return {"name": name, "description": description, "fn": fn}
