# Jupyter Notebooks Guide — BEST Agentic AI Summer Course (2026)

Welcome to the hands-on workspace for the BEST Agentic AI Summer Course. This directory contains the Jupyter notebooks, helper modules, and configuration templates to build agentic architectures from scratch.

---

## 1. Syllabus & Notebooks Overview

| Notebook | Title | Core Topics |
| :--- | :--- | :--- |
| **[00_getting_started.ipynb](file:///home/filpa/repos/best-agentic-ai-course/notebooks/00_getting_started.ipynb)** | Your First AI Call | Basic API configuration, prompt formatting, client instantiation, and mock mode validation. |
| **[01_agent_loop.ipynb](file:///home/filpa/repos/best-agentic-ai-course/notebooks/01_agent_loop.ipynb)** | The Agent Loop | Moving from single-turn requests to the ReAct loop pattern (Thought $\rightarrow$ Action $\rightarrow$ Observation $\rightarrow$ Repeat). |
| **[02_memory_and_rag.ipynb](file:///home/filpa/repos/best-agentic-ai-course/notebooks/02_memory_and_rag.ipynb)** | Memory & RAG | Context limits, conversation summarization, keyword search fallbacks, and Vector Stores (ChromaDB). |
| **[03_planning.ipynb](file:///home/filpa/repos/best-agentic-ai-course/notebooks/03_planning.ipynb)** | Planning & Reasoning | Chain-of-Thought (CoT), plan-then-execute sequences, and task decomposition (linear, parallel, conditional). |
| **[04_reflection.ipynb](file:///home/filpa/repos/best-agentic-ai-course/notebooks/04_reflection.ipynb)** | Reflection & Self-Critique | Reflexion pattern (Generate $\rightarrow$ Evaluate $\rightarrow$ Critique $\rightarrow$ Revise), rubrics, and retry loops. |
| **[05_building_tools.ipynb](file:///home/filpa/repos/best-agentic-ai-course/notebooks/05_building_tools.ipynb)** | Custom Tools & Multi-Agent | Custom tool definition, Model Context Protocol (MCP) servers, Supervisor routing, and Multi-Agent debate. |

---

## 2. Local Setup Guide (Conda / Micromamba)

We recommend using **Micromamba** or **Miniconda** to manage your Python environment.

### Step 1: Create a New Environment
Open your terminal and run:

```bash
# Using micromamba:
micromamba create -n best-agentic-ai python=3.11 -c conda-forge -y

# OR using miniconda:
conda create -n best-agentic-ai python=3.11 -y
```

### Step 2: Activate the Environment
```bash
# Using micromamba:
micromamba activate best-agentic-ai

# OR using miniconda:
conda activate best-agentic-ai
```

### Step 3: Install Dependencies
Navigate to the `notebooks` folder and install packages from [requirements.txt](file:///home/filpa/repos/best-agentic-ai-course/notebooks/requirements.txt):

```bash
pip install -r requirements.txt
```

> [!NOTE]
> `sentence-transformers` requires PyTorch (~2 GB). If you have limited disk space, you can skip PyTorch installation; Notebook 02 will automatically fall back to a keyword-based retrieval method ([simple_rag](file:///home/filpa/repos/best-agentic-ai-course/notebooks/agent_helpers.py#L158)).

### Step 4: Configure API Keys
Copy the example environment configuration file to `.env`:

```bash
cp .env.example .env
```

Open `.env` in a text editor and fill in your API keys (e.g. `OPENAI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`). The notebooks will load these variables automatically.

### Step 5: Start Jupyter Lab
```bash
jupyter lab
```

---

## 3. Google Colab Running Guide

You can run these notebooks in Google Colab for a zero-setup, cloud-hosted environment.

### Step 1: Setup Repository Context
Colab VMs start empty. To use the local helper scripts ([agent_helpers.py](file:///home/filpa/repos/best-agentic-ai-course/notebooks/agent_helpers.py)) and files, clone the repository at the top of your session:

Create a new cell at the very beginning of the notebook and run:
```python
!git clone https://github.com/mihailgavrilita/best-agentic-ai-course.git
%cd best-agentic-ai-course/notebooks
```

### Step 2: Run Notebook Cells
1.  Run the **Setup** cell containing `!pip install ...` to install the required pinned versions in the Colab VM.
2.  Run the subsequent code cells.

### Step 3: Authenticate API Keys
If you do not have a `.env` file uploaded to Colab:
*   The notebooks will automatically request your API keys interactively using `getpass.getpass()`.
*   Alternatively, you can upload your local `.env` file directly using the **Files** tab on the left sidebar of Google Colab.
