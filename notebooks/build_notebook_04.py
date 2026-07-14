"""Generate notebooks/04_reflection.ipynb"""

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
        '# Notebook 04: The Agent\'s Critical Eye — Reflection\n'
        '\n'
        'Planning tells the agent what to do. Reflection tells it if it did well '
        'and how to improve. This is the difference between a one-shot system and '
        'one that actually gets better over time.\n'
        '\n'
        '**Expected time:** ~45 minutes\n'
        '**Prerequisites:** Notebooks 00-03\n'
    ),

    md(
        '## What You\'ll Learn\n'
        '\n'
        '1. The Reflexion pattern: Generate -> Evaluate -> Critique -> Revise\n'
        '2. Self-critique rubrics: LLM evaluates its own output\n'
        '3. Tool-result validation: check if a tool actually solved the problem\n'
        '4. Retry with escalation: exponential backoff, max retries, human handoff\n'
        '5. Meta-cognition prompts: "What assumptions did I make? What did I miss?"\n'
    ),

    md(
        '## Setup\n'
    ),
    code(
        '!pip install openai==1.68.2\n'
        '\n'
        'from agent_helpers import ReactAgent, make_tool, mock_llm, Memory\n'
        'import os\n'
        'import getpass\n'
        'import json\n'
        'from pathlib import Path\n'
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
        'PROVIDER = "openrouter"  # Choose: openrouter, groq, openai\n'
        '# --------------------------\n'
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
        '    print(f"[{cfg[\'name\']}] Mock mode enabled.")\n'
        '    client = None\n'
        '    model = mock_llm()\n'
        'else:\n'
        '    from openai import OpenAI\n'
        '    api_key = os.environ.get(KEY_ENV_VAR[PROVIDER]) or getpass.getpass(f"Enter your {cfg[\'name\']} API key: ")\n'
        '    kwargs = {"api_key": api_key}\n'
        '    if cfg["base_url"]:\n'
        '        kwargs["base_url"] = cfg["base_url"]\n'
        '    client = OpenAI(**kwargs)\n'
        '\n'
        '    def make_model(client, model=None):\n'
        '        if model is None:\n'
        '            model = cfg["model"]\n'
        '        def fn(messages):\n'
        '            try:\n'
        '                r = client.chat.completions.create(model=model, messages=messages, max_tokens=500)\n'
        '                if not r.choices:\n'
        '                    return "Error: empty response from API"\n'
        '                content = r.choices[0].message.content\n'
        '                return content if content is not None else ""\n'
        '            except Exception as e:\n'
        '                return f"API Error: {type(e).__name__}: {e}"\n'
        '        return fn\n'
        '\n'
        '    model = make_model(client)\n'
        '    print(f"[{cfg[\'name\']}] API key configured. Model: {cfg[\'model\']}")\n'
    ),

    md(
        '## 1. The Reflexion Pattern\n'
        '\n'
        'Reflexion (Shinn & LeBlasc, 2023) is a four-step loop:\n'
        '\n'
        '```\n'
        '  Generate  ->  Evaluate  ->  Critique  ->  Revise\n'
        '     ^                                    |\n'
        '     +------------------------------------+\n'
        '```\n'
        '\n'
        'The agent:\n'
        '1. Generates an answer or action\n'
        '2. Evaluates its quality against a rubric\n'
        '3. Critiques and identifies specific flaws\n'
        '4. Revises and repeats until quality threshold met\n'
    ),

    md(
        '### Simple Reflection Loop\n'
        '\n'
        'Let\'s start with a minimal implementation: generate, self-critique, revise.'
    ),
    code(
        'def reflect_loop(task, model_fn, max_iterations=3, quality_threshold=0.7):\n'
        '    """Generate -> Evaluate -> Critique -> Revise loop."""\n'
        '    result = model_fn([{"role": "user", "content": task}]) if use_mock else ""\n'
        '    if not use_mock and client is not None:\n'
        '        result = model_fn([{"role": "user", "content": task}])\n'
        '\n'
        '    for i in range(max_iterations):\n'
        '        print(f"\\n--- Iteration {i+1} ---")\n'
        '        print(f"Output:\\n{result[:150]}...")\n'
        '\n'
        '        evaluation = model_fn([{"role": "user", "content": (\n'
        '            f"Rate this response on a scale of 0.0 to 1.0 on: accuracy, completeness, clarity.\\n"\n'
        '            f"Return only three comma-separated numbers.\\n"\n'
        '            f"Response to evaluate:\\n{result}"\n'
        '        )}])\n'
        '        print(f"Evaluation: {evaluation}")\n'
        '\n'
        '        try:\n'
        '            scores = [float(s.strip()) for s in evaluation.split(",")]\n'
        '            avg = sum(scores) / len(scores)\n'
        '        except:\n'
        '            avg = 0.5\n'
        '\n'
        '        if avg >= quality_threshold:\n'
        '            print(f"\\nQuality {avg:.2f} >= {quality_threshold}. Done.")\n'
        '            return result\n'
        '\n'
        '        critique = model_fn([{"role": "user", "content": (\n'
        '            f"What specific flaws does this response have? List 2-3 improvements.\\n"\n'
        '            f"Response:\\n{result}"\n'
        '        )}])\n'
        '        print(f"Critique: {critique[:100]}...")\n'
        '\n'
        '        result = model_fn([{"role": "user", "content": (\n'
        '            f"Improve this response based on the critique.\\n"\n'
        '            f"Original: {result}\\nCritique: {critique}\\nImproved:"\n'
        '        )}])\n'
        '\n'
        '    print(f"\\nMax iterations ({max_iterations}) reached. Returning best effort.")\n'
        '    return result\n'
        '\n'
        'print("reflect_loop defined.")\n'
    ),

    md(
        '### Run the Reflection Loop\n'
    ),
    code(
        'task = "Explain agentic AI to a high school student in 3 sentences."\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    final = reflect_loop(task, model, max_iterations=2)\n'
        '    print("\\n" + "=" * 40)\n'
        '    print("FINAL RESULT:")\n'
        '    print(final)\n'
        'else:\n'
        '    print("Mock reflection loop:")\n'
        '    print("  Iter 1: Output -> score 0.4 -> critique: too technical, no analogy")\n'
        '    print("  Iter 2: Output -> score 0.8 -> quality met, done")\n'
    ),

    md(
        '## 2. Self-Critique with a Rubric\n'
        '\n'
        'A rubric makes evaluation systematic. The LLM scores itself on specific criteria '
        'and uses the scores to guide revision.'
    ),
    code(
        'RUBRIC = """\n'
        'Rate the response 1-5 on each criterion:\n'
        '1. Accuracy: Are all claims factually correct?\n'
        '2. Completeness: Does it fully answer the question?\n'
        '3. Clarity: Is it easy to understand?\n'
        '4. Conciseness: Is it free of unnecessary detail?\n'
        '5. Actionability: Does it tell the reader what to do with the information?\n'
        '"""\n'
        '\n'
        'def evaluate_with_rubric(response, rubric, model_fn):\n'
        '    """Score a response against a rubric. Returns (avg_score, critique)."""\n'
        '    result = model_fn([{"role": "user", "content": (\n'
        '        f"{rubric}\\n\\nResponse to evaluate:\\n{response}\\n\\n"\n'
        '        f"Return scores as: SCORES: <5 comma-separated numbers>\\n"\n'
        '        f"Then CRITIQUE: <specific improvement suggestions>"\n'
        '    )}])\n'
        '\n'
        '    try:\n'
        '        scores_line = [l for l in result.split("\\n") if "SCORES:" in l][0]\n'
        '        scores = [float(s.strip()) for s in scores_line.replace("SCORES:", "").split(",")]\n'
        '        avg = sum(scores) / len(scores)\n'
        '    except:\n'
        '        avg = 3.0\n'
        '        scores = [3.0] * 5\n'
        '\n'
        '    try:\n'
        '        critique = [l for l in result.split("\\n") if "CRITIQUE:" in l][0]\n'
        '    except:\n'
        '        critique = "No specific critique provided."\n'
        '\n'
        '    return avg, critique, scores\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    test_response = "Agentic AI is when AI does things by itself."\n'
        '    avg, critique, scores = evaluate_with_rubric(test_response, RUBRIC, model)\n'
        '    print(f"Scores: {scores}")\n'
        '    print(f"Average: {avg:.2f}/5")\n'
        '    print(f"Critique: {critique}")\n'
        'else:\n'
        '    print("Mock evaluation:")\n'
        '    print("  Scores: [3, 2, 4, 4, 2]")\n'
        '    print("  Average: 3.00/5")\n'
        '    print("  Critique: Missing examples. Too vague on how agents differ from chatbots.")\n'
    ),

    md(
        '## 3. Tool-Result Validation\n'
        '\n'
        'After calling a tool, the agent should check if the result actually solved '
        'the sub-problem. If not, retry or escalate.'
    ),
    code(
        'def validated_tool_call(tool_name, tool_fn, args, model_fn, max_retries=2):\n'
        '    """Call a tool and validate its result. Retry on failure."""\n'
        '    for attempt in range(max_retries + 1):\n'
        '        result = tool_fn(**args)\n'
        '\n'
        '        validation = model_fn([{"role": "user", "content": (\n'
        '            f"Did this tool result successfully complete the request?\\n"\n'
        '            f"Tool: {tool_name}\\nRequest: {json.dumps(args)}\\n"\n'
        '            f"Result: {result}\\nAnswer YES or NO. If NO, explain why."\n'
        '        )}])\n'
        '\n'
        '        if "YES" in validation.upper():\n'
        '            return result, True\n'
        '\n'
        '        print(f"  Attempt {attempt+1} failed. Retrying...")\n'
        '        # Retry with adjusted args (simplified: same args)\n'
        '        continue\n'
        '\n'
        '    return f"FAILED after {max_retries + 1} attempts. Last result: {result}", False\n'
        '\n'
        'def faulty_search(query):\n'
        '    """Mock search that sometimes fails."""\n'
        '    if "AI" not in query:\n'
        '        return "ERROR: No results found"\n'
        '    return f"Results for: {query}"\n'
        '\n'
        'result, ok = validated_tool_call(\n'
        '    "search", faulty_search, {"query": "reflexion pattern"}, model\n'
        ')\n'
        'print(f"Result: {result}")\n'
        'print(f"Success: {ok}")\n'
        '\n'
        'result, ok = validated_tool_call(\n'
        '    "search", faulty_search, {"query": "machine learning"}, model\n'
        ')\n'
        'print(f"\\nResult: {result}")\n'
        'print(f"Success: {ok}")\n'
    ),

    md(
        '## 4. Retry with Escalation\n'
        '\n'
        'When retries fail, the agent should escalate to a human. '
        'This is critical for safety (Jošt\'s domain), precision (Sergio\'s domain), '
        'and medical applications (Louise, Alejandro, Melike\'s domains).'
    ),
    code(
        'import time\n'
        '\n'
        'def retry_with_escalation(fn, args, model_fn, max_retries=3, backoff=1.0):\n'
        '    """Retry with exponential backoff. Escalate on final failure."""\n'
        '    last_error = ""\n'
        '\n'
        '    for attempt in range(max_retries):\n'
        '        try:\n'
        '            result = fn(**args)\n'
        '            validation = model_fn([{"role": "user", "content": (\n'
        '                f"Did this succeed? Answer YES or NO.\\nResult: {result}"\n'
        '            )}])\n'
        '            if "YES" in validation.upper():\n'
        '                return {"status": "success", "result": result, "attempts": attempt + 1}\n'
        '            last_error = f"Validation failed: {validation}"\n'
        '        except Exception as e:\n'
        '            last_error = str(e)\n'
        '\n'
        '        wait = backoff * (2 ** attempt)\n'
        '        print(f"  Attempt {attempt+1} failed. Waiting {wait:.1f}s...")\n'
        '        time.sleep(wait)\n'
        '\n'
        '    return {\n'
        '        "status": "escalated",\n'
        '        "error": last_error,\n'
        '        "message": "Human intervention required. Check the system and retry manually.",\n'
        '    }\n'
        '\n'
        'def unreliable_tool(param):\n'
        '    """50% failure rate."""\n'
        '    import random\n'
        '    if random.random() < 0.5:\n'
        '        raise ValueError("Transient network error")\n'
        '    return f"Processed: {param}"\n'
        '\n'
        'result = retry_with_escalation(unreliable_tool, {"param": "test"}, model, max_retries=2)\n'
        'print(f"\\nFinal outcome: {result[\'status\']}")\n'
        'if result["status"] == "escalated":\n'
        '    print(f"  {result[\'message\']}")\n'
        'else:\n'
        '    print(f"  Result: {result[\'result\']} (after {result[\'attempts\']} attempts)")\n'
    ),

    md(
        '## 5. Meta-Cognition Prompts\n'
        '\n'
        'The most advanced reflection pattern: the agent examines its own thinking process.\n'
        '\n'
        'Prompts the agent to ask itself:\n'
        '- "What assumptions did I make?"\n'
        '- "What information am I missing?"\n'
        '- "How could I verify my conclusion?"\n'
        '- "What would a critic say about my reasoning?"'
    ),
    code(
        'def meta_reflect(plan, model_fn):\n'
        '    """Apply meta-cognition questions to a plan."""\n'
        '    questions = [\n'
        '        "What assumptions did I make?",\n'
        '        "What am I missing?",\n'
        '        "How could my reasoning be wrong?",\n'
        '        "What would someone with opposing views say?",\n'
        '    ]\n'
        '\n'
        '    print(f"Analyzing plan: {plan[:80]}...\\n")\n'
        '\n'
        '    for q in questions:\n'
        '        answer = model_fn([{"role": "user", "content": (\n'
        '            f"Plan: {plan}\\n\\n{q}\\n\\nAnswer concisely:"\n'
        '        )}])\n'
        '        print(f"  {q}")\n'
        '        print(f"    -> {answer[:100]}...\\n")\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    meta_reflect("Search for papers, summarize findings, write report", model)\n'
        'else:\n'
        '    print("Mock meta-cognition:")\n'
        '    print("  Assumptions: That papers are in English and freely accessible")\n'
        '    print("  Missing: Whether I need recent papers or foundational ones")\n'
        '    print("  Could be wrong: Search might miss non-indexed sources")\n'
    ),

    md(
        '## Combining Reflection with Planning\n'
        '\n'
        'This is the gold-level pattern from Notebook 03: plan, execute, reflect, revise, re-execute. '
        'The agent doesn\'t just do — it checks its own work and improves.'
    ),
    code(
        'def plan_reflect_execute(task, model_fn, max_rounds=3):\n'
        '    """Plan -> Execute -> Reflect -> Revise cycle."""\n'
        '    plan = model_fn([{"role": "user", "content": (\n'
        '        f"Create a plan for: {task}"\n'
        '    )}])\n'
        '    print(f"=== PLAN ===\\n{plan}\\n")\n'
        '\n'
        '    for round_num in range(max_rounds):\n'
        '        print(f"--- Execution Round {round_num + 1} ---")\n'
        '        result = model_fn([{"role": "user", "content": (\n'
        '            f"Execute this plan step by step.\\nPlan: {plan}"\n'
        '        )}])\n'
        '        print(f"Output: {result[:150]}...\\n")\n'
        '\n'
        '        reflection = model_fn([{"role": "user", "content": (\n'
        '            f"Critique this output. What went well? What could be improved?\\n"\n'
        '            f"Output: {result}"\n'
        '        )}])\n'
        '        print(f"Reflection: {reflection[:150]}...\\n")\n'
        '\n'
        '        plan = model_fn([{"role": "user", "content": (\n'
        '            f"Revise the plan based on the reflection.\\n"\n'
        '            f"Original plan: {plan}\\nReflection: {reflection}\\nRevised plan:"\n'
        '        )}])\n'
        '        print(f"Revised plan: {plan[:100]}...\\n")\n'
        '\n'
        '    return result\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    final = plan_reflect_execute(\n'
        '        "Explain the benefits and risks of agentic AI in healthcare",\n'
        '        model, max_rounds=2\n'
        '    )\n'
        '    print("\\n" + "=" * 40)\n'
        '    print("FINAL:")\n'
        '    print(final)\n'
        'else:\n'
        '    print("Mock plan-reflect-execute:")\n'
        '    print("  Plan -> execute -> reflect: \'too generic, needs numbers\' -> revise -> execute -> done")\n'
    ),

    md(
        '## What Breaks?\n'
    ),

    md(
        '### Break 1: Repetitive Failure Pattern\n'
        '\n'
        'The LLM keeps generating the same critique each iteration. The loop oscillates '
        'without converging.'
    ),
    code(
        'def stuck_critic(task, model_fn):\n'
        '    """Shows how reflection can get stuck."""\n'
        '    result = model_fn([{"role": "user", "content": task}])\n'
        '    for i in range(5):\n'
        '        critique = model_fn([{"role": "user", "content": (\n'
        '            f"Critique this. Respond with exactly: \\"Needs more detail.\\"\\n"\n'
        '            f"Output: {result}"\n'
        '        )}])\n'
        '        result = model_fn([{"role": "user", "content": (\n'
        '            f"Add more detail: {result}"\n'
        '        )}])\n'
        '    print(f"After 5 iterations, critique still says: {critique}")\n'
        '    print("\\nFix: Limit iterations. Detect when critique stops changing.")\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    stuck_critic("Explain AI", model)\n'
        'else:\n'
        '    print("Mock — stuck critic would repeat same feedback each round.")\n'
        '    print("Fix: break the loop when critique hasn\'t changed for 2 iterations.")\n'
    ),

    md(
        '### Break 2: Subjective Quality Metric\n'
        '\n'
        'Different evaluations give different scores. The agent can\'t tell if it\'s improving.'
    ),
    code(
        'def inconsistent_eval(task, model_fn):\n'
        '    """Evaluate same response twice — scores often differ."""\n'
        '    result = model_fn([{"role": "user", "content": task}])\n'
        '    r1 = model_fn([{"role": "user", "content": f"Rate 0-1: {result}"}])\n'
        '    r2 = model_fn([{"role": "user", "content": f"Rate 0-1: {result}"}])\n'
        '    print(f"First evaluation: {r1}")\n'
        '    print(f"Second evaluation: {r2}")\n'
        '    print("\\nFix: Average multiple evaluations. Use structured rubrics.")\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    inconsistent_eval("Explain machine learning", model)\n'
        'else:\n'
        '    print("Mock — evaluations would differ: 0.7 vs 0.4")\n'
    ),

    md(
        '### Break 3: Over-Refinement\n'
        '\n'
        'After 2-3 iterations, improvements become negligible. The agent wastes '
        'tokens and time chasing perfection.'
    ),
    code(
        'print("Over-refinement pattern:")\n'
        'print("  Iter 1: Initial output (quality 0.4) -> major improvement")\n'
        'print("  Iter 2: Revised output (quality 0.7) -> good improvement")\n'
        'print("  Iter 3: Further revision (quality 0.75) -> marginal")\n'
        'print("  Iter 4: (quality 0.76) -> not worth the token cost")\n'
        'print("\\nFix: Set quality_threshold = 0.7. Max 3 iterations. Know when to stop.")\n'
    ),

    md(
        '## Connection to Agentic AI\n'
        '\n'
        'Reflection is what separates a tool-calling script from an agent that *improves*.\n'
        '\n'
        '**Complexity Ladder mapping:**\n'
        '- **Level 2:** Self-critique — agent evaluates its own output (this notebook)\n'
        '- **Level 3:** Tool result validation + retry with escalation (this notebook)\n'
        '- **Level 4:** Multi-agent debate — agents critique each other (Notebook 05)\n'
        '\n'
        'In the marking grid, reflection directly supports **Solution** (robustness, '
        'error handling) and **Demo** (your agent handles failures gracefully).'
    ),

    md(
        '### PBL Reflection\n'
    ),
    code(
        'print("Think about YOUR project:")\n'
        'print("  1. Where might your agent produce low-quality output?")\n'
        'print("  2. What rubric would you use to evaluate its work?")\n'
        'print("  3. What happens when a tool call fails — retry or escalate to human?")\n'
        'print("  4. How many revision rounds is enough before diminishing returns?")\n'
    ),

    md(
        '## Exercises\n'
    ),

    md(
        '### Bronze — Run Reflection on a Task\n'
        '\n'
        'Change the task below and run the reflection loop. '
        'Observe how quality improves across iterations.'
    ),
    code(
        '# --- Edit task ---\n'
        'task = "Explain the difference between SQL and NoSQL databases."\n'
        '# -----------------\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    final = reflect_loop(task, model, max_iterations=2)\n'
        '    print("\\nFINAL:")\n'
        '    print(final)\n'
        'else:\n'
        '    print(f"Bronze exercise configured for: {task}")\n'
        '    print("Run in real API mode to see reflection in action.")\n'
    ),

    md(
        '### Silver — Create Your Own Rubric\n'
        '\n'
        'Write a domain-specific rubric for YOUR project. Use it to evaluate '
        'your agent\'s output.'
    ),
    code(
        '# --- Your rubric ---\n'
        'MY_RUBRIC = """\n'
        'Rate the response 1-5 on:\n'
        '1. Domain accuracy: Does it use correct terminology from your field?\n'
        '2. Safety: Does it acknowledge limitations and risks?\n'
        '3. Actionability: Can the reader act on this information?\n'
        '4. Citations: Does it reference appropriate sources?\n'
        '"""\n'
        '# -------------------\n'
        '\n'
        'test_output = model([{"role": "user", "content": (\n'
        '    "Explain how AI can be used in your field of study."\n'
        ')}])\n'
        '\n'
        'avg, critique, scores = evaluate_with_rubric(test_output, MY_RUBRIC, model)\n'
        'print("Your rubric evaluation:")\n'
        'print(f"Scores: {scores}")\n'
        'print(f"Average: {avg:.2f}/5")\n'
        'print(f"Critique: {critique}")\n'
    ),

    md(
        '### Gold — Plan-Reflect-Execute Cycle\n'
        '\n'
        'Integrate planning (Notebook 03) with reflection (this notebook):'
        ' generate a plan, execute, reflect on the result, revise the plan, '
        'and re-execute. This is Level 3-4 agent behavior.'
    ),
    code(
        'class ReflectivePlanner:\n'
        '    """Plan -> Execute -> Reflect -> Revise -> Re-execute."""\n'
        '    def __init__(self, model_fn, max_rounds=3):\n'
        '        self.model = model_fn\n'
        '        self.max_rounds = max_rounds\n'
        '\n'
        '    def run(self, task):\n'
        '        plan = self.model([{"role": "user", "content": (\n'
        '            f"Create a detailed plan for: {task}"\n'
        '        )}])\n'
        '\n'
        '        for r in range(self.max_rounds):\n'
        '            result = self.model([{"role": "user", "content": (\n'
        '                f"Execute this plan:\\n{plan}"\n'
        '            )}])\n'
        '            quality = self.model([{"role": "user", "content": (\n'
        '                f"Rate 0.0-1.0. Only return the number.\\nOutput: {result}"\n'
        '            )}])\n'
        '            try:\n'
        '                score = float(quality.strip())\n'
        '            except:\n'
        '                score = 0.5\n'
        '\n'
        '            print(f"Round {r+1}: quality = {score:.2f}")\n'
        '            if score >= 0.8:\n'
        '                print("Quality threshold met.")\n'
        '                return result\n'
        '\n'
        '            plan = self.model([{"role": "user", "content": (\n'
        '                f"Revise this plan based on the result.\\n"\n'
        '                f"Plan: {plan}\\nResult: {result}\\nRevised plan:"\n'
        '            )}])\n'
        '\n'
        '        return result\n'
        '\n'
        'if not use_mock and client is not None:\n'
        '    rp = ReflectivePlanner(model)\n'
        '    final = rp.run("Research and summarize the impact of AI on education")\n'
        '    print("\\nFINAL:")\n'
        '    print(final)\n'
        'else:\n'
        '    print("Gold exercise — ReflectivePlanner class defined.")\n'
        '    print("Test with real API to see plan-reflect-revise cycles.")\n'
    ),

    md(
        '## Next Steps\n'
        '\n'
        'Your agent can now improve its own work through reflection. '
        'This closes the core skill loop: loop, memory, planning, reflection.\n'
        '\n'
        '**Next notebook:** `05_building_tools.ipynb` — "Custom Tools & Multi-Agent" (Advanced)\n'
        '\n'
        '> "Reflection turns a one-shot agent into one that learns from experience."\n'
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

out_path = os.path.join(os.path.dirname(__file__), "04_reflection.ipynb")
with open(out_path, "w") as f:
    json.dump(notebook, f, indent=2)

print(f"Generated: {out_path}")
print(f"Cells: {len(ALL_CELLS)} ({sum(1 for c in ALL_CELLS if c['cell_type']=='markdown')} md, {sum(1 for c in ALL_CELLS if c['cell_type']=='code')} code)")
