import os
from dotenv import load_dotenv
from strands import Agent
from strands.models.ollama import OllamaModel
from mcp_config import get_github_mcp_client, get_filesystem_mcp_client

load_dotenv()

# Loading system prompt
with open("prompts/system_prompt.txt", "r") as f:
    system_prompt = f.read()

# Initializing Ollama model - qwen2.5
model = OllamaModel(
    model_id="qwen2.5:7b",
    host="http://localhost:11434",
    params={
        "temperature": 0.2,
        "num_ctx": 16384,
    }
)

def analyze_repo(repo_url: str):
    print(f"\n🔍 Analyzing: {repo_url}")
    print("=" * 50)

    # MCP clients as context managers — they start/stop the server process
    with get_github_mcp_client() as github_mcp, \
         get_filesystem_mcp_client() as filesystem_mcp:

        # Get tools from both MCP servers
        github_tools = github_mcp.list_tools_sync()
        filesystem_tools = filesystem_mcp.list_tools_sync()

        print(f"✅ GitHub MCP tools loaded: {[t.tool_name for t in github_tools]}")
        print(f"✅ Filesystem MCP tools loaded: {[t.tool_name for t in filesystem_tools]}")

        # Initialize agent with MCP tools
        agent = Agent(
            model=model,
            system_prompt=system_prompt,
            tools=[*github_tools, *filesystem_tools]
        )

        response = agent(
            f"Analyze this GitHub repository and save a full report: {repo_url}"
        )

        print("\n" + "=" * 50)
        print("✅ Done! Check the reports/ folder.")
        return response

if __name__ == "__main__":
    repo_url = input("Enter GitHub repo URL: ").strip()
    analyze_repo(repo_url)