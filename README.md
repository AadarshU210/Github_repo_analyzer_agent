# 🔍 GitHub Repository Analyst Agent

An autonomous AI agent that analyzes any GitHub repository and generates a structured report — powered by **Strands Agents**, **MCP (Model Context Protocol)**, and a switchable LLM backend.

---

## What it does

Give it a GitHub repo URL and it autonomously:

- Fetches repo metadata, README, file structure, open issues and recent commits
- Reasons over all gathered data using an LLM
- Writes a structured markdown report covering code health, activity, issues and contributor insights
- Saves the report locally with a one-click download from the UI

All tool usage happens via **real MCP servers** — the agent decides what to fetch and in what order on its own.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | [Strands Agents SDK](https://github.com/strands-agents/sdk) |
| Tool Protocol | [MCP — Model Context Protocol](https://modelcontextprotocol.io) |
| GitHub Data | `@modelcontextprotocol/server-github` |
| File I/O | `@modelcontextprotocol/server-filesystem` |
| Default LLM | Ollama — `qwen2.5:7b` (local, free) |
| UI | Streamlit |

---

## Model Providers

The agent supports three LLM backends — switch between them from the sidebar in the UI. Only the provider config changes; everything else stays identical.

| Provider | Model | Cost |
|---|---|---|
| **Ollama (Local)** | `qwen2.5:7b` | Free |
| **Anthropic API** | `claude-3-5-haiku` | Pay per use |
| **AWS Bedrock** | `claude-3-5-haiku` via Bedrock | Pay per use |

---

## Project Structure

```
github-analyst/
├── agent.py                # CLI entry point
├── app.py                  # Streamlit UI
├── mcp_config.py           # MCP server connections
├── model_config.py         # Model provider switcher
├── requirements.txt
├── .env.example            # env template
├── prompts/
│   └── system_prompt.txt   # Agent instructions + report structure
├── reports/                # Generated reports saved here
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Node.js 18+ (required for MCP servers via `npx`)
- [Ollama](https://ollama.com) installed and running locally
- `qwen2.5:7b` pulled in Ollama

```bash
ollama pull qwen2.5:7b
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/Github_repo_analyzer_agent.git
cd Github_repo_analyzer_agent
```

**2. Create and activate virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and fill in your values:
```
GITHUB_TOKEN=your_github_token_here

# Only needed if using Anthropic provider
ANTHROPIC_API_KEY=your_anthropic_key_here

# Only needed if using AWS Bedrock provider
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

To get a GitHub token → GitHub Settings → Developer Settings → Personal Access Tokens → Generate new token (classic) → select `repo` scope.

---

## Running the App

**Streamlit UI (recommended)**
```bash
streamlit run app.py
```

**CLI mode**
```bash
python agent.py
```

---

## How it works

```
You enter a repo URL
        │
        ▼
Strands Agent starts
        │
        ├── connects to GitHub MCP server  (npx, Node.js process)
        ├── connects to Filesystem MCP server (npx, Node.js process)
        │
        ▼
Agent autonomously decides:
  → fetch repo info
  → fetch README
  → fetch file structure
  → fetch open issues
  → fetch recent commits
  → fetch contributors
        │
        ▼
LLM reasons over all data
        │
        ▼
Structured report saved to reports/
+ displayed in UI with download button
        │
        ▼
💬 Chat with the agent about the repo
```

---

## Upgrade Path

This project is structured to demonstrate provider-agnostic agent architecture:

```
v1  →  Strands + Ollama (local, free)         ✅ current
v2  →  Strands + Anthropic API                 swap 1 line in model_config.py
v3  →  Strands + AWS Bedrock                   swap 1 line in model_config.py
```

---

## Example Report Output

```
# Repository Analysis Report: facebook/react

## Overview
React is a JavaScript library for building user interfaces...

## README Analysis
...

## Codebase Structure
...

## Issues Analysis
...

## Recent Activity
...

## Top Contributors
...

## Final Verdict
Health Score: 9/10
Strengths: ...
Areas for Improvement: ...
```

---

## Notes

- Context window is set to 16k. For very large repos the agent may truncate some content.
- `qwen2.5:7b` is recommended over `llama3.2` for reliable tool calling behaviour.
