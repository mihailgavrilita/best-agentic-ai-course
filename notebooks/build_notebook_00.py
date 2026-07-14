"""Generate notebooks/00_getting_started.ipynb"""

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


def code(source: str, outputs: list | None = None) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": CELL_META,
        "outputs": outputs or [],
        "source": [source],
    }


def code_no_exec(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"tags": ["skip-execution"]},
        "outputs": [],
        "source": [source],
    }


cells = [
    # ---- Title ----
    md(
        '# Notebook 00: Your First AI Call\n'
        '\n'
        'Welcome! This notebook gets your environment ready and makes your first LLM call. '
        'No agentic concepts yet — just setup and confidence-building.\n'
        '\n'
        '**Expected time:** ~20 minutes\n'
        '**Prerequisites:** Python 3.10+, pip\n'
    ),

    # ---- What you will learn ----
    md(
        '## What You\'ll Learn\n'
        '\n'
        '1. Confirm your Python environment works\n'
        '2. Install required packages\n'
        '3. Choose and configure an LLM provider (OpenAI, DeepSeek, Groq, or OpenRouter)\n'
        '4. Make your first LLM call\n'
        '5. Compare how different prompts change the output\n'
        '6. Handle common errors\n'
    ),

    # ---- Install ----
    md(
        '## Setup: Install Dependencies\n'
        '\n'
        'Run the cell below to install everything needed for this notebook.'
    ),
    code(
        '!pip install openai==1.68.2 groq==0.18.0\n'
    ),

    # ---- Env check ----
    md(
        '## Step 1: Environment Check\n'
        '\n'
        'Run this to verify Python and key packages are ready.'
    ),
    code(
        'import sys\n'
        'import importlib\n'
        '\n'
        'print(f"Python version: {sys.version}")\n'
        'print(f"Python executable: {sys.executable}")\n'
        '\n'
        'required = ["openai", "groq"]\n'
        'for pkg in required:\n'
        '    try:\n'
        '        mod = importlib.import_module(pkg)\n'
        '        ver = getattr(mod, "__version__", "unknown")\n'
        '        print(f"  {pkg}: {ver}  OK")\n'
        '    except ImportError:\n'
        '        print(f"  {pkg}: NOT FOUND — run the install cell above")\n'
        '\n'
        'print("\\nEnvironment check complete.")\n'
    ),

    # ---- Provider selection intro ----
    md(
        '## Step 2: Choose Your Provider\n'
        '\n'
        'This notebook supports **4 LLM providers**. Pick one below:\n'
        '\n'
        '| Provider | SDK | Model | Get API Key |\n'
        '|----------|-----|-------|------------|\n'
        '| **OpenAI** | `openai` | `gpt-4o-mini` | https://platform.openai.com/api-keys |\n'
        '| **DeepSeek** | `openai` (compatible) | `deepseek-chat` | https://platform.deepseek.com/api_keys |\n'
        '| **Groq** | `groq` | `llama-3.3-70b-versatile` | https://console.groq.com/keys |\n'
        '| **OpenRouter** | `openai` (compatible) | `nvidia/nemotron-3-ultra-550b-a55b:free` | https://openrouter.ai/keys |\n'
        '\n'
        'Each provider has its own **mock flag** below. Set yours to `True` if you have no API key for that provider.\n'
        '\n'
        '> **Using .env?** Copy `.env.example` to `.env` and fill in your keys. '
        'The notebook auto-loads keys from `.env` so you never paste them in code.\n'
        '> **No API keys at all?** Leave all `MOCK` flags `True`. The mock LLM returns a canned response so you can follow along.'
    ),

    # ---- Provider config cell ----
    code(
        'import os\n'
        'import getpass\n'
        'from pathlib import Path\n'
        'from openai import OpenAI\n'
        'from groq import Groq\n'
        '\n'
        '# --- Optional .env file loading (no extra pip installs needed) ---\n'
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
        '    print("  Tip: cp .env.example .env  and fill in your keys to skip prompts.")\n'
        '\n'
        '# --- Pick your provider ---\n'
        'PROVIDER = "openai"  # Choose: openai, deepseek, groq, openrouter\n'
        '# --------------------------\n'
        '\n'
        '# Per-provider mock flags (True = use canned response, no API key needed)\n'
        'MOCK = {\n'
        '    "openai":     True,\n'
        '    "deepseek":   True,\n'
        '    "groq":       True,\n'
        '    "openrouter": True,\n'
        '}\n'
        '\n'
        '# Environment variable names for auto-loading keys (set in .env)\n'
        'KEY_ENV_VAR = {\n'
        '    "openai":     "OPENAI_API_KEY",\n'
        '    "deepseek":   "DEEPSEEK_API_KEY",\n'
        '    "groq":       "GROQ_API_KEY",\n'
        '    "openrouter": "OPENROUTER_API_KEY",\n'
        '}\n'
        '\n'
        '# Provider configuration table\n'
        'CONFIG = {\n'
        '    "openai": {\n'
        '        "name": "OpenAI",\n'
        '        "pkg": "openai",\n'
        '        "model": "gpt-4o-mini",\n'
        '        "key_url": "https://platform.openai.com/api-keys",\n'
        '        "client_fn": lambda k: OpenAI(api_key=k),\n'
        '        "mock_response": "Silicon dreams stir\\n Circuits learn in silent hum\\n Minds of code awake.",\n'
        '    },\n'
        '    "deepseek": {\n'
        '        "name": "DeepSeek",\n'
        '        "pkg": "openai",\n'
        '        "model": "deepseek-chat",\n'
        '        "key_url": "https://platform.deepseek.com/api_keys",\n'
        '        "client_fn": lambda k: OpenAI(api_key=k, base_url="https://api.deepseek.com"),\n'
        '        "mock_response": "Deep thought stirs\\n  Patterns emerge in silicon sea\\n  Mind awakens.",\n'
        '    },\n'
        '    "groq": {\n'
        '        "name": "Groq",\n'
        '        "pkg": "groq",\n'
        '        "model": "llama-3.3-70b-versatile",\n'
        '        "key_url": "https://console.groq.com/keys",\n'
        '        "client_fn": lambda k: Groq(api_key=k),\n'
        '        "mock_response": "Fast inference\\n  LLM responds at lightning speed\\n  Groq hardware hums.",\n'
        '    },\n'
        '    "openrouter": {\n'
        '        "name": "OpenRouter",\n'
        '        "pkg": "openai",\n'
        '        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",\n'
        '        "key_url": "https://openrouter.ai/keys",\n'
        '        "client_fn": lambda k: OpenAI(api_key=k, base_url="https://openrouter.ai/api/v1"),\n'
        '        "mock_response": "Nemotron thinks deep\\n  Ultra-scale reasoning flows\\n  Knowledge unbound.",\n'
        '    },\n'
        '}\n'
        '\n'
        'cfg = CONFIG[PROVIDER]\n'
        'use_mock = MOCK[PROVIDER]\n'
        '\n'
        'if use_mock:\n'
        '    print(f"[{cfg[\'name\']}] Mock mode enabled. Using canned responses.")\n'
        '    client = None\n'
        'else:\n'
        '    try:\n'
        '        importlib = __import__("importlib")\n'
        '        importlib.import_module(cfg["pkg"])\n'
        '    except ImportError:\n'
        '        print(f\'Package \\\'{cfg["pkg"]}\\\' not installed. Run the install cell above.\')\n'
        '        print("Falling back to mock mode.")\n'
        '        client = None\n'
        '        use_mock = True\n'
        '    else:\n'
        '        api_key = os.environ.get(KEY_ENV_VAR[PROVIDER]) or getpass.getpass(f"Enter your {cfg[\'name\']} API key: ")\n'
        '        client = cfg["client_fn"](api_key)\n'
        '        print(f"[{cfg[\'name\']}] API key configured.")\n'
    ),

    # ---- Validate ----
    md(
        '### Validate Your Connection\n'
        '\n'
        'This makes a tiny test call to confirm your key and provider work together.'
    ),
    code(
        'if not use_mock and client is not None:\n'
        '    try:\n'
        '        response = client.chat.completions.create(\n'
        '            model=cfg["model"],\n'
        '            messages=[{"role": "user", "content": "Say OK and nothing else."}],\n'
        '            max_tokens=10,\n'
        '        )\n'
        '        print(f"Connection valid. Response: {response.choices[0].message.content}")\n'
        '    except Exception as e:\n'
        '        print(f"Validation FAILED: {type(e).__name__}: {e}")\n'
        '        print(f"Check your key at {cfg[\'key_url\']}")\n'
        'else:\n'
        '    print(f"[{cfg[\'name\']}] Mock mode — skipping validation.")\n'
    ),

    # ---- First LLM call ----
    md(
        '## Step 3: Your First LLM Call\n'
        '\n'
        'Let\'s make a real call. We\'ll ask the model to write a haiku.'
    ),
    code(
        'if not use_mock and client is not None:\n'
        '    response = client.chat.completions.create(\n'
        '        model=cfg["model"],\n'
        '        messages=[\n'
        '            {"role": "user", "content": "Write a haiku about artificial intelligence."}\n'
        '        ],\n'
        '    )\n'
        '    reply = response.choices[0].message.content\n'
        '    print("LLM response:")\n'
        '    print(reply)\n'
        '    print(f"\\n---\\nModel used: {response.model}")\n'
        '    print(f"Tokens: {response.usage.total_tokens} (input: {response.usage.prompt_tokens}, output: {response.usage.completion_tokens})")\n'
        'else:\n'
        '    reply = cfg["mock_response"]\n'
        '    print(f"[{cfg[\'name\']}] MOCK response:")\n'
        '    print(reply)\n'
    ),

    # ---- Response structure ----
    md(
        '### Inspecting the Response\n'
        '\n'
        'The API returns a structured object. Let\'s look at its parts.'
    ),
    code(
        'if not use_mock and client is not None:\n'
        '    response = client.chat.completions.create(\n'
        '        model=cfg["model"],\n'
        '        messages=[{"role": "user", "content": "Say hello world."}],\n'
        '    )\n'
        '    print("Full response object fields:")\n'
        '    print(f"  id: {response.id}")\n'
        '    print(f"  model: {response.model}")\n'
        '    print(f"  created: {response.created}")\n'
        '    print(f"  role: {response.choices[0].message.role}")\n'
        '    print(f"  content: {response.choices[0].message.content}")\n'
        '    print(f"  finish_reason: {response.choices[0].finish_reason}")\n'
        '    print(f"  total_tokens: {response.usage.total_tokens}")\n'
        'else:\n'
        '    print(f"[{cfg[\'name\']}] Mock mode — response object not available.")\n'
        '    print("\\nReal response contains: id, model, created, choices[].message.content, usage")\n'
    ),

    # ---- Prompt engineering teaser ----
    md(
        '## Step 4: Prompt Engineering Teaser\n'
        '\n'
        'The same model gives different answers depending on *how* you ask. '
        'Let\'s compare short vs. detailed prompts.'
    ),
    code(
        'if not use_mock and client is not None:\n'
        '    prompts = [\n'
        '        "What is agentic AI?",\n'
        '        "Explain agentic AI to a first-year university student. Use an analogy. Keep it under 100 words.",\n'
        '    ]\n'
        '    for i, prompt in enumerate(prompts, 1):\n'
        '        print(f"--- Prompt {i}: \\"{prompt}\\" ---")\n'
        '        response = client.chat.completions.create(\n'
        '            model=cfg["model"],\n'
        '            messages=[{"role": "user", "content": prompt}],\n'
        '        )\n'
        '        print(response.choices[0].message.content)\n'
        '        print(f"(Tokens: {response.usage.total_tokens})\\n")\n'
        'else:\n'
        '    print(f"[{cfg[\'name\']}] Mock mode:")\n'
        '    print("  Prompt 1 (short): Agentic AI is AI that can take actions beyond just generating text.")\n'
        '    print("  Prompt 2 (detailed): Imagine a librarian who doesn\'t just answer questions but actually goes to find the book, opens it, and reads you the relevant page. That\'s agentic AI.")\n'
    ),
    code(
        'if not use_mock and client is not None:\n'
        '    print("--- With vs. Without System Prompt ---")\n'
        '    \n'
        '    r1 = client.chat.completions.create(\n'
        '        model=cfg["model"],\n'
        '        messages=[{"role": "user", "content": "Explain gradient descent in 2 sentences."}],\n'
        '    )\n'
        '    print("No system prompt:")\n'
        '    print(r1.choices[0].message.content)\n'
        '    \n'
        '    r2 = client.chat.completions.create(\n'
        '        model=cfg["model"],\n'
        '        messages=[\n'
        '            {"role": "system", "content": "You are a physics professor. Use precise mathematical language."},\n'
        '            {"role": "user", "content": "Explain gradient descent in 2 sentences."},\n'
        '        ],\n'
        '    )\n'
        '    print("\\nWith system prompt (physics professor):")\n'
        '    print(r2.choices[0].message.content)\n'
        'else:\n'
        '    print(f"[{cfg[\'name\']}] Mock mode:")\n'
        '    print("  Without: Gradient descent iteratively adjusts parameters to minimize a loss function.")\n'
        '    print("  With: Let us consider the gradient operator ∇ acting on the loss surface L(θ)...")\n'
    ),

    # ---- Troubleshooting ----
    md(
        '## Troubleshooting: Common Errors\n'
        '\n'
        'Let\'s break things on purpose so you recognize the errors when they happen.'
    ),

    md(
        '### Error 1: Missing or Invalid API Key\n'
        '\n'
        'What happens when you pass a bad key?'
    ),
    code(
        'bad_client = OpenAI(api_key="sk-bad-key")\n'
        'try:\n'
        '    bad_client.chat.completions.create(\n'
        '        model="gpt-4o-mini",\n'
        '        messages=[{"role": "user", "content": "hello"}],\n'
        '    )\n'
        'except Exception as e:\n'
        '    print(f"Error type: {type(e).__name__}")\n'
        '    print(f"Error message: {e}")\n'
        '    print("\\nFix: Generate a valid key at the provider\'s API key page.")\n'
    ),

    md(
        '### Error 2: Wrong Model Name\n'
        '\n'
        'Model names are exact strings. A typo = an error.'
    ),
    code(
        'if not use_mock and client is not None:\n'
        '    try:\n'
        '        client.chat.completions.create(\n'
        '            model="gpt-4o-mini",  # intentional typo: should match cfg["model"]\n'
        '            messages=[{"role": "user", "content": "hello"}],\n'
        '        )\n'
        '    except Exception as e:\n'
        '        print(f"Error type: {type(e).__name__}")\n'
        '        print(f"Error message: {e}")\n'
        '        print("\\nFix: Check the model name in cfg[\'model\'] against provider docs.")\n'
        'else:\n'
        '    print(f"[{cfg[\'name\']}] Mock mode — skipping error demo.")\n'
        '    print("In real mode you\'d see an error like: NotFoundError or BadRequestError")\n'
    ),

    md(
        '### Error 3: Empty Messages\n'
        '\n'
        'The API requires at least one message.'
    ),
    code(
        'if not use_mock and client is not None:\n'
        '    try:\n'
        '        client.chat.completions.create(\n'
        '            model=cfg["model"],\n'
        '            messages=[],\n'
        '        )\n'
        '    except Exception as e:\n'
        '        print(f"Error type: {type(e).__name__}")\n'
        '        print(f"Error message: {e}")\n'
        '        print("\\nFix: Always include at least one message in the messages list.")\n'
        'else:\n'
        '    print(f"[{cfg[\'name\']}] Mock mode — skipping error demo.")\n'
    ),

    # ---- Exercises ----
    md(
        '## Exercises\n'
        '\n'
        'Choose your tier. Bronze is run-only (no coding). Silver modifies existing code. '
        'Gold builds something new.\n'
    ),

    md(
        '### Bronze — Run and Observe\n'
        '\n'
        'Run the cell below. It makes 3 different prompts automatically using your chosen provider. '
        'Observe how the output changes.'
    ),
    code(
        'if not use_mock and client is not None:\n'
        '    topics = [\n'
        '        "machine learning",\n'
        '        "database systems",\n'
        '        "cybersecurity",\n'
        '    ]\n'
        '    for topic in topics:\n'
        '        response = client.chat.completions.create(\n'
        '            model=cfg["model"],\n'
        '            messages=[{\n'
        '                "role": "user",\n'
        '                "content": f"Define {topic} in one sentence for a beginner."\n'
        '            }],\n'
        '        )\n'
        '        print(f"{topic}: {response.choices[0].message.content}\\n")\n'
        'else:\n'
        '    print(f"[{cfg[\'name\']}] Mock mode responses:")\n'
        '    print("  machine learning: Teaching computers to learn from data without explicit instructions.")\n'
        '    print("  database systems: Organized collections of data with efficient storage and retrieval.")\n'
        '    print("  cybersecurity: Protecting systems, networks, and data from digital attacks.")\n'
    ),

    md(
        '### Silver — Change the Model and Provider\n'
        '\n'
        'Edit the `PROVIDER`, `model` (in `CONFIG`), and prompt variables below. '
        'Try a different provider or model. Try a prompt from your own domain.'
    ),
    code(
        '# --- Edit these lines ---\n'
        'silver_provider = "openai"      # Try: deepseek, groq, openrouter\n'
        'silver_model = "gpt-4o-mini"    # Must match the provider\'s available models\n'
        'silver_prompt = "Explain why agentic AI matters for biomedical research."\n'
        '# --------------------------\n'
        '\n'
        'silver_cfg = CONFIG.get(silver_provider)\n'
        'if silver_cfg is None:\n'
        '    print(f"Unknown provider: {silver_provider}")\n'
        'elif MOCK.get(silver_provider, True):\n'
        '    print(f"[{silver_cfg[\'name\']}] Mock mode — skipping real call.")\n'
        '    print(f"Model: {silver_model}")\n'
        '    print(f"Prompt: {silver_prompt}")\n'
        '    print("[Mock] In real mode, you\'d see the actual response here.")\n'
        'else:\n'
        '    try:\n'
        '        importlib.import_module(silver_cfg["pkg"])\n'
        '        silver_key = getpass.getpass(f"Enter {silver_cfg[\'name\']} API key: ")\n'
        '        silver_client = silver_cfg["client_fn"](silver_key)\n'
        '        print(f"Using: {silver_cfg[\'name\']} / {silver_model}")\n'
        '        print(f"Prompt: {silver_prompt}\\n")\n'
        '        response = silver_client.chat.completions.create(\n'
        '            model=silver_model,\n'
        '            messages=[{"role": "user", "content": silver_prompt}],\n'
        '        )\n'
        '        print(response.choices[0].message.content)\n'
        '    except Exception as e:\n'
        '        print(f"Error: {type(e).__name__}: {e}")\n'
    ),

    md(
        '### Gold — Compare All Four Providers\n'
        '\n'
        'Create clients for all 4 providers (mock or real). Ask the same question to each. '
        'Compare verbosity, tone, and content across providers.'
    ),
    code(
        'gold_question = "What are the ethical risks of autonomous AI agents?"\n'
        '\n'
        'for prov_id, prov_cfg in CONFIG.items():\n'
        '    name = prov_cfg["name"]\n'
        '    print(f"--- {name} ---")\n'
        '    if MOCK.get(prov_id, True):\n'
        '        print(f"[Mock] Would respond to: {gold_question[:50]}...")\n'
        '        print()\n'
        '        continue\n'
        '    try:\n'
        '        importlib.import_module(prov_cfg["pkg"])\n'
        '        pk = getpass.getpass(f"Enter {name} API key: ")\n'
        '        prov_client = prov_cfg["client_fn"](pk)\n'
        '        resp = prov_client.chat.completions.create(\n'
        '            model=prov_cfg["model"],\n'
        '            messages=[{"role": "user", "content": gold_question}],\n'
        '        )\n'
        '        print(resp.choices[0].message.content)\n'
        '        print(f"(Tokens: {resp.usage.total_tokens})\\n")\n'
        '    except Exception as e:\n'
        '        print(f"Error: {type(e).__name__}: {e}\\n")\n'
    ),

    # ---- Exit link ----
    md(
        '## Next Steps\n'
        '\n'
        'You\'ve confirmed your environment works and made your first LLM calls. '
        'You\'ve seen how prompts change output and tried multiple providers.\n'
        '\n'
        '**Next notebook:** `01_agent_loop.ipynb` — "The Agent Loop"\n'
        '\n'
        '> "Now that you can call an LLM, let\'s make it loop."\n'
    ),
]


notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": KERNEL_SPEC,
        "language_info": LANG_INFO,
    },
    "nbformat": NB_VERSION,
    "nbformat_minor": NB_MINOR,
}

out_path = os.path.join(os.path.dirname(__file__), "00_getting_started.ipynb")
with open(out_path, "w") as f:
    json.dump(notebook, f, indent=2)

print(f"Generated: {out_path}")
