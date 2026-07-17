# Useful Links & Resources

A curated collection of resources organized by course topic. Each section maps to one or more notebooks.

---

## Getting Started & LLM Basics

> **Notebook 00** — Your First AI Call

| Resource | Description |
|----------|-------------|
| [OpenAI Platform](https://platform.openai.com/api-keys) | API keys and docs for GPT models |
| [DeepSeek Platform](https://platform.deepseek.com/api_keys) | API keys and docs for DeepSeek |
| [Groq Console](https://console.groq.com/keys) | API keys for fast inference |
| [OpenRouter](https://openrouter.ai/keys) | Access multiple models through one API |
| [Prompt Engineering Guide](https://www.promptingguide.ai/) | Community guide to writing effective prompts |
| [AI: A Modern Approach](https://aima.cs.berkeley.edu/) | Russell & Norvig's classic AI textbook — the theoretical foundation for the concepts in this course |

---

## The Agent Loop & Architecture

> **Notebook 01** — The Agent Loop

| Resource | Description |
|----------|-------------|
| [AI Agents in 2026: Tools, Memory, Evals, Guardrails](https://andriifurmanets.com/blogs/ai-agents-2026-practical-architecture-tools-memory-evals-guardrails) | Practical blueprint for agent systems — the agent loop, tool calling, memory, and guardrails |
| [ReAct: Synergizing Reasoning and Acting](https://arxiv.org/abs/2210.03629) | Foundational paper on the ReAct pattern (Thought → Action → Observation) |
| [LangChain](https://www.langchain.com/) | Framework for building LLM apps with tool use |
| [LangGraph](https://langchain-ai.github.io/langgraph/) | Stateful agent workflows — built for agent loops |
| [CrewAI](https://www.crewai.com/) | Framework for orchestrating role-playing AI agents |

---

## Memory & RAG

> **Notebook 02** — The Agent's Mind

| Resource | Description |
|----------|-------------|
| [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag/) | Step-by-step RAG implementation |
| [ChromaDB Getting Started](https://docs.trychroma.com/docs/overview/getting-started) | Zero-config vector database used in the course |
| [Sentence Transformers](https://www.sbert.net/) | Embedding library for semantic search |
| [LangChain Memory Concepts](https://python.langchain.com/docs/concepts/memory/) | Overview of memory types: buffer, summary, entity |

---

## Planning & Reasoning

> **Notebook 03** — The Agent's Brain

| Resource | Description |
|----------|-------------|
| [Tree of Thoughts (Yao et al., 2023)](https://arxiv.org/abs/2305.10601) | Deliberate problem solving — explores multiple reasoning paths instead of left-to-right generation |
| [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) | Original paper on step-by-step reasoning in LLMs |
| [Lilian Weng: LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) | Excellent overview of planning, memory, and tool use in agents |

---

## Reflection & Self-Critique

> **Notebook 04** — The Agent's Critical Eye

| Resource | Description |
|----------|-------------|
| [Reflexion (Shinn & LeBlanc, 2023)](https://arxiv.org/abs/2303.11366) | Language agents with verbal reinforcement learning — the generate → evaluate → critique → revise loop |
| [Self-Refine (Madaan et al., 2023)](https://arxiv.org/abs/2303.17651) | Iterative refinement with self-feedback |
| [Building Effective Agents (Anthropic)](https://www.anthropic.com/engineering/building-effective-agents) | When to use agents vs. workflows, and how to add reflection |

---

## Tools, Skills & MCP

> **Notebook 05** — Custom Tools & Multi-Agent

### Model Context Protocol (MCP)

| Resource | Description |
|----------|-------------|
| [MCP Official Documentation](https://modelcontextprotocol.io/) | Spec and docs for the Model Context Protocol — "USB-C for AI" |
| [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) | Build MCP servers and clients in Python |
| [MCP Servers Repository](https://github.com/modelcontextprotocol/servers) | Official and community MCP server implementations |

### Skills & Agent Configuration

| Resource | Description |
|----------|-------------|
| [How to Write Good AGENTS.md Files](https://www.augmentcode.com/blog/how-to-write-good-agents-dot-md-files) | What makes AGENTS.md files effective — good ones give quality jumps equivalent to model upgrades |
| [Using Skills with Deep Agents](https://www.langchain.com/blog/using-skills-with-deep-agents) | How skills (SKILL.md folders) reduce token usage vs. traditional tools |
| [Hermes Agent Skills Catalog](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog#email) | Catalog of bundled agent skills — shows the skill pattern in action |

### Open Source Agent Projects

| Resource | Description |
|----------|-------------|
| [oh-my-opencode](https://github.com/opensoft/oh-my-opencode) | OpenCode plugin with subagents, curated tools, and MCPs |
| [Hiring Agent](https://github.com/interviewstreet/hiring-agent) | Resume evaluation agent — parses PDFs, enriches with GitHub data, produces scored evaluations |

---

## Problem-Based Learning (PBL)

> The course follows a PBL approach — you learn by solving a real problem, not by following instructions.

| Resource | Description |
|----------|-------------|
| [Aalborg University PBL Model](https://www.en.aau.dk/about-aau/profile/pbl) | The PBL tradition this course follows — team-based, project-driven learning |

---

## Context Engineering

| Resource | Description |
|----------|-------------|
| [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | How to manage context windows, memory, and prompt construction for agents |

---

## YouTube Videos

| Video | Description |
|-------|-------------|
| [AI Agents 2026](https://youtu.be/9FuNtfsnRNo?si=t6eU7XpPXPtft-Fh) | Overview of the current AI agent landscape |
| [Agent Architecture Deep Dive](https://youtu.be/UhRGHr7pgnU?si=CaiUV-tv1v0CJGhB) | Walkthrough of agent system design |
| [Building AI Agents](https://youtu.be/RairMJflUSA?si=HcjFvhZvwfY6CzSR) | Practical guide to building and deploying agents |

---

## Libraries Used in This Course

| Library | Purpose | Notebook |
|---------|---------|----------|
| `openai` | OpenAI-compatible API client | 00–05 |
| `groq` | Groq API client (fast inference) | 00–01 |
| `langchain` | LLM application framework | 02–05 |
| `langgraph` | Stateful agent workflows | 02 |
| `chromadb` | Vector database for RAG | 02 |
| `sentence-transformers` | Embedding models | 02 |
| `mcp` | Model Context Protocol SDK | 05 |

---

*Last updated: July 2026*
