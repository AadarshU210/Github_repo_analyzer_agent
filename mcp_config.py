import os
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# Github MCP Server
def get_github_mcp_client():
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-github"
                ],
                env={
                    **os.environ,
                    "GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")
                }
            )
        )
    )

# FileSystem MCP server
def get_filesystem_mcp_client():
    reports_path = os.path.abspath("./reports")
    os.makedirs(reports_path, exist_ok=True)
    return MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    reports_path
                ],
                env=os.environ
            )
        )
    )